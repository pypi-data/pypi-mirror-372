import sys,os,re,time
from typing import Any
import pyautogui
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.event.Event import Event

class Keyboard(Event):

  def _trigger(self)->Any:
    time.sleep(0.5)
    if sys.platform == "darwin":
      pyautogui.press('enter')
      time.sleep(0.5)
    pyautogui.press('esc')