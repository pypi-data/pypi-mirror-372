import pyperclip

class BluesOS():
  
  @classmethod
  def copy(cls):
    # copy from the os's clip board
    return pyperclip.paste()
  
  @classmethod
  def write(cls,text):
    pyperclip.copy(text)

  @classmethod
  def clear(cls):
    BluesOS.write('')