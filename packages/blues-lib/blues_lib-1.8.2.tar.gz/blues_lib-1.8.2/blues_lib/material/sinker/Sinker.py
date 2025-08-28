import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from blues_lib.material.MatHandler import MatHandler
from type.output.STDOut import STDOut
from dao.material.MatMutator import MatMutator 

class Sinker(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    config = self._config.get('sinker')
    if not config:
      return STDOut(200,'no sinker config')

    self._method = config.get('method','insert')
    conditions:list[dict] = self._config.get('conditions')
    
    sink_entities:list[dict] = self._get_sink_entities(config)
    
    # insert to the db
    if self._method == 'insert':
      return MatMutator().insert(sink_entities)
    elif self._method == 'update':
      return MatMutator().update(sink_entities,conditions)
    elif self._method == 'delete':
      return MatMutator().delete(conditions)
    else:
      self._logger.warning(f'[{self.__class__.__name__}] Skip to upsert - {self._method} is not supported')
      return STDOut(200,f'no support method: {self._method}')
    
  def _get_sink_entities(self,config:dict)->list[dict]:

    entity = config.get('entity') # the merged fields
    inc_fields = config.get('inc_fields')
    exc_fields = config.get('dec_fields')
    sink_entities:list[dict] = []
    
    for entity in self._entities:
      sink_entity:dict = entity.copy()
      # merge the entity
      if entity:
        sink_entity.update(entity)
        
      # include and exclude the fields
      if inc_fields:
        sink_entity = {k:v for k,v in sink_entity.items() if k in inc_fields}
      if exc_fields:
        sink_entity = {k:v for k,v in sink_entity.items() if k not in exc_fields}

      # filter the unmat fields
      sink_entity = self._get_mat_entity(sink_entity)

      sink_entities.append(sink_entity)
    return sink_entities
    

