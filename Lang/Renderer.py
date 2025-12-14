"""
/*******************************************************************
*                  2D Renderer for the Lang Language               *
*                                                                  *
*    PROGRAMMER: Ethan Nelson                                      *
*    COURSE: CS340 Program Language Design                         *
*    DATE: 12/13/25                                                *
*    REQUIREMENT: Assignment extension                             *
*                                                                  *
*    DESCRIPTION:                                                  *
*    Provides a built-in Renderer class for 2D graphics using      *
*    PyQt6 QGraphicsView. Supports drawing basic shapes (circle,   *
*    rectangle, line) that can be animated by binding to Lang      *
*    variables. Embeds directly into PyQt6 GUI.                    *
*                                                                  *
*    COPYRIGHT:                                                    *
*    This code is copyright (c)2025 Ethan Nelson and Dean Zeller.  *
*                                                                  *
*    CREDITS:                                                      *
*    ChatGPT                                                       *
*                                                                  *
*******************************************************************/
"""

from typing import Dict, List, Tuple, Optional, Any
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsLineItem
from PyQt6.QtCore import Qt, QTimer, QRectF, QLineF
from PyQt6.QtGui import QColor, QBrush, QPen


class LangRenderer:
    """
    2D renderer using PyQt6 QGraphicsView for embedded graphics.
    Shapes are tied to variable names for continuous animation.
    """
    _instance: Optional['LangRenderer'] = None

    """
        /**********************************************************
        * METHOD: __new__                                         *
        * DESCRIPTION: Enforce singleton instance creation         *
        * PARAMETERS: cls (type)                                  *
        * RETURN VALUE: LangRenderer                              *
        **********************************************************/
    """
    def __new__(cls) -> 'LangRenderer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    """
        /**********************************************************
        * METHOD: __init__                                        *
        * DESCRIPTION: Initialize renderer state (singleton-safe)  *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.scene: Optional[QGraphicsScene] = None
        self.view: Optional[QGraphicsView] = None
        self.shapes: Dict[int, Dict[str, Any]] = {}  # id -> shape info dict
        self.variables_ref: Optional[Dict[str, int]] = None
        self._shape_counter: int = 0
        self._bg_color: Tuple[int, int, int] = (30, 30, 40)
        self._width: int = 800
        self._height: int = 450
        self._timer: Optional[QTimer] = None
        self._is_initialized: bool = False

    """
        /**********************************************************
        * METHOD: set_view                                        *
        * DESCRIPTION: Bind a QGraphicsView and create a scene     *
        * PARAMETERS: view (QGraphicsView)                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def set_view(self, view: QGraphicsView) -> None:
        self.view = view
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    """
        /**********************************************************
        * METHOD: init                                            *
        * DESCRIPTION: Initialize scene dimensions and background  *
        * PARAMETERS: width (int), height (int)                   *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def init(self, width: int = 800, height: int = 450) -> None:
        self._width = width
        self._height = height
        
        if self.scene is None:
            self.scene = QGraphicsScene()
        
        # Set scene rectangle (0,0 at top-left, y increases downward)
        self.scene.setSceneRect(0, 0, width, height)
        
        # Apply background color
        self.scene.setBackgroundBrush(QBrush(QColor(*self._bg_color)))
        
        if self.view is not None:
            self.view.setScene(self.scene)
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        self._is_initialized = True

    """
        /**********************************************************
        * METHOD: background                                      *
        * DESCRIPTION: Set background color (RGB or grayscale)     *
        * PARAMETERS: r (int), g (int|None), b (int|None)          *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def background(self, r: int, g: int = None, b: int = None) -> None:
        if g is None and b is None:
            # Grayscale
            self._bg_color = (r, r, r)
        else:
            self._bg_color = (r, g if g is not None else 0, b if b is not None else 0)
        
        if self.scene is not None:
            self.scene.setBackgroundBrush(QBrush(QColor(*self._bg_color)))

    """
        /**********************************************************
        * METHOD: draw                                            *
        * DESCRIPTION: Draw a shape tied to Lang variables         *
        * PARAMETERS: shape_type (str), x_var (str), y_var (str),  *
        *             size (int), width (int), height (int),       *
        *             r (int), g (int), b (int),                   *
        *             x2_var (str|None), y2_var (str|None)         *
        * RETURN VALUE: int (shape_id)                             *
        **********************************************************/
    """
    def draw(self, shape_type: str, x_var: str, y_var: str, 
             size: int = 20, width: int = 40, height: int = 30,
             r: int = 255, g: int = 255, b: int = 255,
             x2_var: str = None, y2_var: str = None) -> int:
        if self.scene is None:
            raise RuntimeError("Renderer not initialized. Call Renderer.init() first.")
        
        shape_color = QColor(r, g, b)
        brush = QBrush(shape_color)
        pen = QPen(shape_color)
        pen.setWidth(2)
        
        # Get initial position from variables or default to center
        init_x = self._width // 2
        init_y = self._height // 2
        if self.variables_ref:
            init_x = self.variables_ref.get(x_var, init_x)
            init_y = self.variables_ref.get(y_var, init_y)
        
        item: Optional[QGraphicsItem] = None
        shape_info: Dict[str, Any] = {
            'type': shape_type,
            'x_var': x_var,
            'y_var': y_var,
        }
        
        if shape_type == "circle":
            # QGraphicsEllipseItem uses bounding rect, so center it
            item = QGraphicsEllipseItem(0, 0, size * 2, size * 2)
            item.setBrush(brush)
            item.setPen(QPen(Qt.PenStyle.NoPen))
            item.setPos(init_x - size, init_y - size)
            shape_info['size'] = size
            
        elif shape_type == "rectangle":
            item = QGraphicsRectItem(0, 0, width, height)
            item.setBrush(brush)
            item.setPen(QPen(Qt.PenStyle.NoPen))
            item.setPos(init_x - width // 2, init_y - height // 2)
            shape_info['width'] = width
            shape_info['height'] = height
            
        elif shape_type == "line":
            init_x2 = init_x + 50
            init_y2 = init_y
            if self.variables_ref and x2_var and y2_var:
                init_x2 = self.variables_ref.get(x2_var, init_x2)
                init_y2 = self.variables_ref.get(y2_var, init_y2)
            
            item = QGraphicsLineItem(QLineF(init_x, init_y, init_x2, init_y2))
            item.setPen(pen)
            shape_info['x2_var'] = x2_var
            shape_info['y2_var'] = y2_var
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
        
        self.scene.addItem(item)
        
        # Store shape with its variable bindings
        shape_id = self._shape_counter
        self._shape_counter += 1
        shape_info['item'] = item
        self.shapes[shape_id] = shape_info
        
        return shape_id

    """
        /**********************************************************
        * METHOD: _update_shapes                                  *
        * DESCRIPTION: Update shape positions from variable values *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def _update_shapes(self) -> None:
        if self.variables_ref is None:
            return
        
        for shape_id, info in self.shapes.items():
            item = info['item']
            x_var = info['x_var']
            y_var = info['y_var']
            shape_type = info['type']
            
            x_val = self.variables_ref.get(x_var, None)
            y_val = self.variables_ref.get(y_var, None)
            
            if x_val is None or y_val is None:
                continue
            
            if shape_type == "circle":
                size = info['size']
                item.setPos(x_val - size, y_val - size)
                
            elif shape_type == "rectangle":
                w = info['width']
                h = info['height']
                item.setPos(x_val - w // 2, y_val - h // 2)
                
            elif shape_type == "line":
                x2_var = info.get('x2_var')
                y2_var = info.get('y2_var')
                x2_val = self.variables_ref.get(x2_var, x_val + 50) if x2_var else x_val + 50
                y2_val = self.variables_ref.get(y2_var, y_val) if y2_var else y_val
                item.setLine(QLineF(x_val, y_val, x2_val, y2_val))

    """
        /**********************************************************
        * METHOD: start_animation                                 *
        * DESCRIPTION: Start timer-based shape updates (~60 FPS)   *
        * PARAMETERS: variables_dict (Dict[str,int]),             *
        *             update_callback (callable|None)             *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def start_animation(self, variables_dict: Dict[str, int], update_callback=None) -> None:
        self.variables_ref = variables_dict
        self._update_callback = update_callback
        
        if self._timer is None:
            self._timer = QTimer()
            self._timer.timeout.connect(self._on_timer_tick)
        
        self._timer.start(16)  # ~60 FPS

    """
        /**********************************************************
        * METHOD: _on_timer_tick                                  *
        * DESCRIPTION: Per-frame callback to update animation      *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def _on_timer_tick(self) -> None:
        if self._update_callback:
            self._update_callback()
        self._update_shapes()

    """
        /**********************************************************
        * METHOD: stop_animation                                  *
        * DESCRIPTION: Stop the animation timer                   *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def stop_animation(self) -> None:
        if self._timer is not None:
            self._timer.stop()

    """
        /**********************************************************
        * METHOD: clear                                           *
        * DESCRIPTION: Remove all shapes from the scene            *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def clear(self) -> None:
        if self.scene is not None:
            for shape_id, info in list(self.shapes.items()):
                self.scene.removeItem(info['item'])
        self.shapes.clear()
        self._shape_counter = 0

    """
        /**********************************************************
        * METHOD: reset                                           *
        * DESCRIPTION: Reset renderer to initial state             *
        * PARAMETERS: None                                        *
        * RETURN VALUE: None                                      *
        **********************************************************/
    """
    def reset(self) -> None:
        self.stop_animation()
        self.clear()
        self._bg_color = (30, 30, 40)
        self._is_initialized = False
        if self.scene is not None:
            self.scene.setBackgroundBrush(QBrush(QColor(*self._bg_color)))

    """
        /**********************************************************
        * METHOD: is_initialized                                  *
        * DESCRIPTION: Check whether init() has been called        *
        * PARAMETERS: None                                        *
        * RETURN VALUE: bool                                      *
        **********************************************************/
    """
    def is_initialized(self) -> bool:
        return self._is_initialized


# Global singleton instance for use by Interpreter
_renderer: Optional[LangRenderer] = None


"""
    /**********************************************************
    * METHOD: get_renderer                                    *
    * DESCRIPTION: Get or create the singleton renderer        *
    * PARAMETERS: None                                        *
    * RETURN VALUE: LangRenderer                              *
    **********************************************************/
"""
def get_renderer() -> LangRenderer:
    global _renderer
    if _renderer is None:
        _renderer = LangRenderer()
    return _renderer


"""
    /**********************************************************
    * METHOD: reset_renderer                                  *
    * DESCRIPTION: Reset and clear the singleton renderer      *
    * PARAMETERS: None                                        *
    * RETURN VALUE: None                                      *
    **********************************************************/
"""
def reset_renderer() -> None:
    global _renderer
    if _renderer is not None:
        _renderer.reset()
    _renderer = None
