"""Load/verify a history snapshot with no GUI access or model inference."""
import logging
from pathlib import Path
from PIL import Image
from core.inference_engine import _OwnedWorkerThread
from core.image_budget import validate_raster_budget
from core.image_source import analysis_identity, load_verified_image
from data.artifact_integrity import verify_saved_artifacts, record_artifact_paths

logger = logging.getLogger(__name__)


class HistoryLoadWorker(_OwnedWorkerThread):
    def __init__(self, database, record_id, parse_analysis, parse_classification, parent=None):
        super().__init__(parent)
        self.database, self.record_id = database, record_id
        self.parse_analysis, self.parse_classification = parse_analysis, parse_classification
        self.prepared = None
        self.error_message = None
        self.outcome = None

    def check_cancelled(self):
        if self.isInterruptionRequested():
            raise InterruptedError('History loading cancelled.')

    def _image(self, path, mode):
        self.check_cancelled()
        if not path:
            return None
        try:
            with Image.open(path) as image:
                validate_raster_budget(image.size)
                return image.convert(mode).copy()
        except (OSError, ValueError, Image.DecompressionBombError):
            logger.warning('Saved image could not be decoded: %s', path)
            return None

    def run(self):
        try:
            self.check_cancelled()
            record = self.database.get_record_by_id(self.record_id)
            if record is None:
                raise ValueError(f'Record #{self.record_id} could not be found.')
            analysis = self.parse_analysis(record)
            if record.get('task_type') == 'classification':
                self.parse_classification(record)
            verified = verify_saved_artifacts(analysis, record_artifact_paths(record), check_cancelled=self.check_cancelled)
            original, source_identity, source_problem = None, None, ''
            try:
                path = record.get('image_path') or ''
                if not Path(path).is_file():
                    raise ValueError(f'Original image not found: {path or "unknown file"}')
                original, source_identity = load_verified_image(path, analysis_identity(analysis),
                    require_identity=True, check_cancelled=self.check_cancelled)
            except InterruptedError:
                raise
            except (OSError, ValueError, Image.DecompressionBombError) as error:
                source_problem = str(error)
            result = self._image(record.get('result_image_path'), 'RGBA')
            color_path = record.get('result_color_mask_path')
            colors = self._image(color_path, 'RGB') if color_path else None
            # Legacy tiled records sometimes retained only the result PNG.
            if colors is None and not color_path and record.get('task_type') == 'classification':
                colors = result.convert('RGB') if result is not None else None
            self.check_cancelled()
            # Bind decoded output pixels to the hashes too, not just a pre-read check.
            if verified:
                verify_saved_artifacts(analysis, record_artifact_paths(record), check_cancelled=self.check_cancelled)
            self.prepared = dict(record=record, analysis=analysis, artifacts_verified=verified,
                original=original, source_identity=source_identity, source_problem=source_problem,
                stored_image=result, color_map=colors)
            self.outcome = 'ready'
        except InterruptedError:
            self.outcome = 'cancelled'
        except Exception as error:
            logger.exception('History loading failed')
            self.error_message = str(error) or 'The saved history result could not be loaded.'
            self.outcome = 'error'
