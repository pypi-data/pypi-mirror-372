import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.CommandName import CommandName
from type.output.STDOut import STDOut
from command.NodeCommand import NodeCommand
from material.privatizer.Localizer import Localizer

class Privatizer(NodeCommand):

  NAME = CommandName.Material.PRIVATIZER
  TYPE = CommandName.Type.SETTER
  
  def _setup(self)->bool:
    super()._setup()
    if not self._output or not self._output.data:
      raise Exception(f'[{self.NAME}] mat entities is None')

  def _invoke(self)->STDOut:
    request = {
      'model':self._node_input,
      'entities':self._output.data,
    }
    return Localizer(request).handle()