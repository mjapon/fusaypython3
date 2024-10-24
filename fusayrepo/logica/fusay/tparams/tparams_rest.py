from fusayrepo.logica.fusay.tparams.tparam_service import TParamService
from fusayrepo.utils.pyramidutil import TokenView
from cornice.resource import resource


@resource(collection_path='/api/params', path='/api/params/{tprm_id}', cors_origins=('*',))
class TParamsRest(TokenView):

    def collection_get(self):
        accion = self.get_rqpa()
        service = TParamService(self.dbsession)
        if accion == 'listar':
            filtro = self.get_request_param('filtro')
            estado = self.get_request_param('estado')
            seccion = self.get_request_param('seccion')
            result = service.find(filtro, userid=self.get_user_id(), estado=estado, seccion=seccion)
            return self.res200({'params': result})
        elif accion == 'form':
            form = service.get_form_crea()
            return self.res200({'form': form})

    def put(self):
        body = self.get_json_body()
        service = TParamService(self.dbsession)
        service.update(form=body, userupd=self.get_user_id())
        return self.res200({'msg': 'Actualización exitosa'})

    def post(self):
        body = self.get_json_body()
        service = TParamService(self.dbsession)
        service.crear(form=body, usercrea=self.get_user_id())
        return self.res200({'msg': 'Registro exitoso'})
