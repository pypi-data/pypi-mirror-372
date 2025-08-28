import sys,os,re,time
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from behavior.bean.Bean import Bean
from util.BluesOS import BluesOS

class Copy(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    # clear before click the copy button
    BluesOS.clear() 
    self._browser.action.mouse.click(**kwargs)
    time.sleep(0.5)
    return BluesOS.copy()
