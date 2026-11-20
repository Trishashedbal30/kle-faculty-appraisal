"""Track plug-ins change report emphasis, never the institution's scoring rules."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Specialist:
    category:str|None
    focus:str
    def highlights(self,items):
        selected=[r for r in items if self.category is None or r['category']==self.category]
        return [{'record_id':r['id'],'title':r['title'],'category':r['category'],'source':r['locator']} for r in selected[:8]]
REGISTRY={
    'balanced':Specialist(None,'Review evidence across research, teaching and institutional service.'),
    'teaching':Specialist('teaching','Review teaching load, aggregate feedback and learning-outcome evidence.'),
    'research':Specialist('research','Review publications, projects, grants and guidance evidence.'),
    'administrative':Specialist('administrative','Review documented duties, committee work and institutional service.')}

def register(name,specialist):
    if name in REGISTRY:raise ValueError('A registered track cannot be silently replaced.')
    REGISTRY[name]=specialist
