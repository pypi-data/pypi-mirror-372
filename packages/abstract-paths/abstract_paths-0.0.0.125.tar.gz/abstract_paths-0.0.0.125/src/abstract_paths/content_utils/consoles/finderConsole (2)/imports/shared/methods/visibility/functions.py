from PyQt6.QtWidgets import (
    QSizePolicy, QWidget, QLayout, QToolButton
    )
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import QPropertyAnimation

def set_visible(self, name: str, visible: bool):
    sec = self._sections.get(name)
    if not sec:
        return
    btn: QToolButton = sec["button"]
    if btn.isChecked() != visible:
        btn.setChecked(visible)  # this triggers toggle handler

def is_visible(self, name: str) -> bool:
    sec = self._sections.get(name)
    return bool(sec and sec["button"].isChecked())

def button(self, name: str) -> QToolButton | None:
    sec = self._sections.get(name)
    return sec["button"] if sec else None

def container(self, name: str) -> QWidget | None:
    sec = self._sections.get(name)
    return sec["container"] if sec else None
# ---- public API ----
def register(self, *,
             name: str,
             container: QWidget | QLayout,
             button: QToolButton | None = None,
             start_visible: bool | None = None,
             animate: bool | None = None,
             shortcut: str | None = None,
             button_host_layout: QLayout | None = None,
             button_text_open: str = "−",    # Unicode minus
             button_text_closed: str = "+",
             persist: bool = True) -> QToolButton:
    """
    Register a collapsible section.
    - name: unique key
    - container: QWidget or QLayout (layout will be wrapped)
    - button: optional QToolButton; one will be created if None
    - start_visible: override initial visibility (else restored from settings or True)
    - animate: override default slide animation
    - shortcut: optional keyboard shortcut to toggle
    - button_host_layout: where to inject auto-created button (if provided)
    - persist: remember state via QSettings
    Returns the toggle button.
    """
    if isinstance(container, QLayout):
        container = wrap_layout(container)

    if button is None:
        button = QToolButton(self._owner)
        button.setCheckable(True)
        button.setAutoRaise(True)
        button.setToolTip(f"Toggle {name}")
        if button_host_layout is not None:
            button_host_layout.addWidget(button)

    key = f"section/{name}/visible"
    anim = self._animate_default if animate is None else animate

    # restore persisted state
    if start_visible is None:
        vis = self._settings.value(key, True, type=bool) if persist else True
    else:
        vis = bool(start_visible)

    # prepare container for animation if needed
    animator = None
    if anim:
        container.setSizePolicy(QSizePolicy.Policy.Preferred,
                                QSizePolicy.Policy.Fixed)
        container.setMaximumHeight(10**6)  # ensure correct initial measurement
        animator = QPropertyAnimation(container, b"maximumHeight", self)
        animator.setDuration(self._anim_ms)
        animator.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

    # initial state
    button.setChecked(vis)
    button.setText(button_text_open if vis else button_text_closed)
    if not anim:
        container.setVisible(vis)
    else:
        # jump to target height without anim at startup
        container.setVisible(True)
        target = container.sizeHint().height() if vis else 0
        container.setMaximumHeight(target)
        container.setVisible(vis)

    # connect behavior
    def _apply(checked: bool):
        # label
        button.setText(button_text_open if checked else button_text_closed)
        # animate or instant
        if anim:
            # make sure visible to measure during open
            container.setVisible(True)
            start_h = container.maximumHeight()
            end_h = container.sizeHint().height() if checked else 0
            animator.stop()
            animator.setStartValue(start_h)
            animator.setEndValue(end_h)
            animator.finished.disconnect() if animator.receivers(animator.finished) else None

            def _after():
                # hide after collapsing to remove from tab focus
                if end_h == 0:
                    container.setVisible(False)
            animator.finished.connect(_after)
            animator.start()
        else:
            container.setVisible(checked)

        if persist:
            self._settings.setValue(key, checked)
        self.toggled.emit(name, checked)

        # resize parent a bit (optional)
        if self._owner:
            self._owner.adjustSize()

    button.toggled.connect(_apply)

    # optional shortcut
    if shortcut:
        QShortcut(QKeySequence(shortcut), self._owner,
                            activated=lambda: button.toggle())

    # store
    self._sections[name] = dict(
        container=container, button=button, animator=animator,
        text_open=button_text_open, text_closed=button_text_closed,
        key=key, persist=persist, animate=anim
    )
    return button
