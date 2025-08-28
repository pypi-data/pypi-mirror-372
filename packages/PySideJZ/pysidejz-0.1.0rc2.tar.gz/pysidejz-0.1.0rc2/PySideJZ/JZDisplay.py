import numpy as np
from loguru import logger
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QImage, QMouseEvent, QPainter, QPixmap, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QWidget

from PySideJZ.JZAbvs import JZAbvs

# default width and height are just placeholders, actual values set by the user of the class
DEFAULT_W = 640
DEFAULT_H = 480

FIT_PADDING = 0.02  # padding to fit the pixmap into the view, to avoid cropping
DISPLAY_MAX_ZOOM = 25.0  # maximum zoom factor for the display
DISPLAY_MIN_ZOOM = 0.01  # minimum zoom factor for the display
ZOOM_IN_SCALE = 1.1  # scale factor for zooming in
ZOOM_OUT_SCALE = 0.9  # scale factor for zooming out


class JZDisplay(QGraphicsView):
    """JZDisplay is a custom QGraphicsView that handles video display and interaction."""

    fit_image = Signal()
    white_noise = Signal()
    reset = Signal()
    update_image = Signal(np.ndarray)
    update_misc_image = Signal(np.ndarray)
    update_transparent_image = Signal(np.ndarray)
    start_blinking_pixmap = Signal(QGraphicsPixmapItem, int)
    stop_blinking_pixmap = Signal()
    resize_scene = Signal(int, int)

    def __init__(self, parent: QWidget, w: int = DEFAULT_W, h: int = DEFAULT_H) -> None:
        super().__init__(parent, mouseTracking=True, objectName="JZDisplay")

        self._mouse_pos = None
        self._mouse_press_pos = None

        self._w = w
        self._h = h

        self._scene = QGraphicsScene(0, 0, self._w, self._h, parent=self)
        self.setScene(self._scene)
        self.setSizePolicy(JZAbvs.Policy.MINEX, JZAbvs.Policy.MINEX)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

        self.pixmap = QGraphicsPixmapItem()
        self.pixmap_misc = QGraphicsPixmapItem()
        self.pixmap_transparent = QGraphicsPixmapItem()
        self.pixmap_to_blink: QGraphicsPixmapItem | None = None
        self._pixmap_timer: QTimer | None = None

        self._scene.addItem(self.pixmap)
        self._scene.addItem(self.pixmap_misc)
        self._scene.addItem(self.pixmap_transparent)

        self.fit_image.connect(self._on_fit_into_view)
        self.white_noise.connect(self._on_white_noise)
        self.reset.connect(self._reset)
        self.update_image.connect(self._on_image)
        self.update_misc_image.connect(self._on_misc_image)
        self.update_transparent_image.connect(self._on_transparent_image)
        self.start_blinking_pixmap.connect(self._start_blinking_pixmap)
        self.stop_blinking_pixmap.connect(self._stop_blinking_pixmap)
        self.resize_scene.connect(self._change_scene_dimensions)

        self.fit_image.emit()
        self.reset.emit()
        self.resize_scene.emit(self._w, self._h)

    def resize(self) -> None:
        """Must be called by parent upon resizing the widget."""
        self.fit_image.emit()

    @Slot()
    def _reset(self) -> None:
        """Set all of the pixmaps to be blank, reset the screen, stop blinking."""
        self.pixmap.setPixmap(QPixmap())
        self.pixmap_misc.setPixmap(QPixmap())
        self.pixmap_transparent.setPixmap(QPixmap())

        if self._pixmap_timer:
            self.stop_blinking()

        self._on_gray_screen()

    @Slot(int, int)
    def _change_scene_dimensions(self, w: int, h: int) -> None:
        """Change the dimensions of the scene to fit the new width and height."""
        self._scene.setSceneRect(0, 0, w, h)
        self._reset()
        self._w = w
        self._h = h

    @Slot()
    def _on_fit_into_view(self) -> None:
        """Resize the scene so that the pixmap takes up the whole view."""
        w = self.size().width()
        h = self.size().height()
        scene_w = self.sceneRect().width()
        scene_h = self.sceneRect().height()
        scale_x = w / scene_w
        scale_y = h / scene_h

        factor = min(max(min(scale_x, scale_y) - FIT_PADDING, DISPLAY_MIN_ZOOM), DISPLAY_MAX_ZOOM)
        self.resetTransform()
        self.scale(factor, factor)

    @Slot(np.ndarray)
    def _on_image(self, image: np.ndarray) -> None:
        """Set the image to the pixmap and fit it into the view."""
        if image.ndim == 2:  # noqa: PLR2004
            image = self.grayscale_to_rgb(image)
        pixmap = self._np_array_to_pixmap(image)
        self.pixmap.setPixmap(pixmap)

    @Slot(np.ndarray)
    def _on_misc_image(self, image: np.ndarray) -> None:
        """Set the misc image to the pixmap."""
        if image.ndim == 2:  # noqa: PLR2004
            image = self.grayscale_to_rgb(image)
        pixmap = self._np_array_to_pixmap(image)
        self.pixmap_misc.setPixmap(pixmap)

    @Slot(np.ndarray)
    def _on_transparent_image(self, image: np.ndarray) -> None:
        """Set the transparent image to the pixmap."""
        if image.shape[2] != 4:  # noqa: PLR2004
            raise ValueError("Image must be a 4-channel RGBA image for transparency.")
        pixmap = self._np_array_to_pixmap(image, img_format=QImage.Format.Format_RGBA8888)
        self.pixmap_transparent.setPixmap(pixmap)

    @Slot()
    def _on_white_noise(self) -> None:
        """Generate white noise image and set it to the pixmap."""
        rng = np.random.default_rng()
        image = rng.integers(0, 255, (self._h, self._w, 3), dtype=np.uint8)
        pixmap = self._np_array_to_pixmap(image)
        self.pixmap.setPixmap(pixmap)

    @Slot()
    def _on_gray_screen(self) -> None:
        """Generate gray screen image and set it to the pixmap."""
        image = np.full((self._h, self._w, 3), 128, dtype=np.uint8)
        pixmap = self._np_array_to_pixmap(image)
        self.pixmap.setPixmap(pixmap)

    def _np_array_to_pixmap(
        self,
        image: np.ndarray,
        img_format: QImage.Format = QImage.Format.Format_RGB888,
    ) -> QPixmap:
        """Convert numpy array to QPixmap that would be displayable by the JZDisplay."""

        h, w = image.shape[:2]
        bytes_per_line = w * 3

        # handle special case, we allow image to be transparent
        if img_format == QImage.Format.Format_RGBA8888:
            qimg = QImage(image.data, w, h, img_format)
        else:
            qimg = QImage(image.data, w, h, bytes_per_line, img_format)
        return QPixmap.fromImage(qimg)

    @Slot(QMouseEvent)
    def mouseMoveEvent(self, event: QMouseEvent):
        """Capture the mouse press position and set the cursor to arrow."""
        pos = self.mapToScene(event.pos())
        x, y = int(pos.x()), int(pos.y())
        if (not 0 <= x < self._w) or (not 0 <= y < self._h):
            self._mouse_pos = None
        else:
            self._mouse_pos = (x, y)
        return super().mouseMoveEvent(event)

    @Slot(QMouseEvent)
    def mousePressEvent(self, event: QMouseEvent):
        """Capture the mouse press position and set the cursor to arrow."""
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        pos = self.mapToScene(event.pos())
        x, y = int(pos.x()), int(pos.y())
        if (not 0 <= x < self._w) or (not 0 <= y < self._h):
            self._mouse_press_pos = None
        else:
            self._mouse_press_pos = (x, y)
        logger.debug(f"Mouse pressed at {self._mouse_press_pos}")
        super().mousePressEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    @Slot(QMouseEvent)
    def mouseReleaseEvent(self, event):
        """Reset the mouse press position and set the cursor to arrow."""
        super().mouseReleaseEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    @Slot(QWheelEvent)
    def wheelEvent(self, event):
        """Rescales the current image according to mouse scroll direction."""
        scale = self.transform().m11()
        if event.angleDelta().y() > 0:
            factor = 1 if scale > DISPLAY_MAX_ZOOM else ZOOM_IN_SCALE
        else:
            factor = 1 if scale < DISPLAY_MIN_ZOOM else ZOOM_OUT_SCALE
        self.scale(factor, factor)

    def start_blinking(self, pixmap: QGraphicsPixmapItem, interval_ms: int) -> None:
        """Start blinking the pixmap at the specified interval."""
        self.start_blinking_pixmap.emit(pixmap, interval_ms)

    @Slot(QGraphicsPixmapItem, int)
    def _start_blinking_pixmap(self, pixmap: QGraphicsPixmapItem, interval_ms: int) -> None:
        """Start blinking the pixmap at the specified interval.

        This was created to be able to blink the bad pixel map overlayed on top of the image,
        but can be done with any pixmap for any reason."""
        if self._pixmap_timer:
            raise RuntimeError("A pixmap is already blinking. Stop it before starting a new one.")

        self._pixmap_timer = QTimer(self)
        self._pixmap_timer.setInterval(interval_ms)
        self._pixmap_timer.timeout.connect(self._blink_pixmap)
        self._pixmap_to_blink = pixmap
        self._pixmap_timer.start()

    def stop_blinking(self) -> None:
        """Stop blinking the pixmap."""
        self.stop_blinking_pixmap.emit()

    @Slot()
    def _stop_blinking_pixmap(self) -> None:
        """Stop blinking the pixmap."""
        if not self._pixmap_timer:
            return

        self._pixmap_timer.stop()
        self._pixmap_timer.deleteLater()
        self._pixmap_timer = None

        if self._pixmap_to_blink:
            self._pixmap_to_blink.setVisible(False)
            self._pixmap_to_blink = None

    @Slot()
    def _blink_pixmap(self) -> None:
        """Toggle the visibility of the pixmap to create a blinking effect."""
        if not self._pixmap_to_blink:
            return
        pixmap = self._pixmap_to_blink
        pixmap.setVisible(not pixmap.isVisible())

    def grayscale_to_rgb(self, image: np.ndarray) -> np.ndarray:
        """Convert the given image from grayscale to RGB.

        Not using cv2.cvtColor to avoid unnecessary dependencies, cv2 is very heavy, and it is
        only place where it is used. The numpy code below is equivalent."""
        if image.ndim != 2:  # noqa: PLR2004
            raise ValueError("Input image must be a 2D grayscale image.")
        return np.stack((image,) * 3, axis=-1)




