from Ferramentas_Producao.modules.dsgTools.processing.processing import Processing
from qgis import core, gui
import processing
import json

class RuleStatistics(Processing):
    
    def __init__(self, mediator):
        super(RuleStatistics, self).__init__()
        self.processingId = 'dsgtools:rulestatistics'

    def run(self, parameters):
        proc = super().run(parameters)
        if 'OUTPUT' in proc and proc['OUTPUT']:
            html = ''
            for line in proc['OUTPUT'].split('\n\n'):
                if '[regras]' in line.lower():
                    html+='<h3>{0}</h3>'.format(line)
                elif 'passaram' in line.lower():
                    html += u"<p style=\"color:green\">{0}</p>".format(line)
                else:
                    html += u"<p style=\"color:red\">{0}</p>".format(line)
            return html
        return "<p style=\"color:red\">{0}</p>".format(
            'Não há regras para as camadas carregadas!'
        )
        
    def getParameters(self, parameters):
        parameters = { 
            'INPUT_LAYERS' : [
                self.getLayerUriFromTable(layerData['schema'], layerData['nome'])
                for layerData in parameters['layers']
            ],
            'RULEFILE' : '.json', 
            'RULEDATA' : json.dumps(parameters['rules']) 
        }