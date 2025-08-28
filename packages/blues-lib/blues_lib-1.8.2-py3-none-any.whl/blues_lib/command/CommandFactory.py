import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.factory.Factory import Factory
from type.executor.Command import Command
from namespace.CommandName import CommandName

# control
from command.control.Blocker import Blocker
from command.control.Retryer import Retryer
from command.control.Printer import Printer

# browser
from command.browser.Creator import Creator

# crawler
from command.crawler.Engine import Engine

# material
from command.material.Formatter import Formatter
from command.material.Privatizer import Privatizer
from command.material.Sink import Sink
from command.material.Querier import Querier

# notifier
from command.notifier.Email import Email

# --- flow command ---
# flow
from command.flow.Engine import Engine as FlowEngine

class CommandFactory(Factory):

  _COMMANDS:dict[str,Command] = {
    
    # control
    Blocker.NAME:Blocker,
    Retryer.NAME:Retryer,
    Printer.NAME:Printer,
    
    # browser
    Creator.NAME:Creator,
    
    # crawler
    Engine.NAME:Engine,
    
    # material
    Formatter.NAME:Formatter,
    Privatizer.NAME:Privatizer,
    Sink.NAME:Sink,
    Querier.NAME:Querier,
    
    # notifier
    Email.NAME:Email,

    # flow command
    FlowEngine.NAME:FlowEngine,
  }
  
  def __init__(self,context:dict,input:dict) -> None:
    self._context = context
    self._input = input
    
  def create(self,name:CommandName)->Command | None:
    # overide
    cmd = self._COMMANDS.get(name)
    return cmd(self._context,self._input) if cmd else None

