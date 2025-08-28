import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Command import Command
from crawler.MatCrawler import MatCrawler
from namespace.CommandName import CommandName

class Page(Command):
  
  NAME = CommandName.Material.PAGE

  def execute(self):

    cr_model = self._context['input'].get('crawler')
    browser = self._context['browser'].data
    if not cr_model or not browser:
      self._logger.info(f'[{self.NAME}] Skip this command - no crawler model or browser')
      return

    crawler = MatCrawler(cr_model,browser)
    stdout = crawler.crawl()
    self._context['crawler'] = stdout

    if stdout.code!=200 or not stdout.data:
      raise Exception(f'[{self.NAME}] Failed to crawl available entities!')
    else:
      self._logger.info(f'[{self.NAME}] Managed to crawl available entities!')


