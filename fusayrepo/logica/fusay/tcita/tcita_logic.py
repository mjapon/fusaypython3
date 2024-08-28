from fusayrepo.utils.pyramidutil import PyramidView


class TCitaLogic(PyramidView):
    def get_form(self, tcitadao):
        pac_id = self.get_request_param('pac')
        tipocita = self.get_request_param('tipocita')
        form = tcitadao.get_form(pac_id=pac_id)
        horas = tcitadao.get_horas_for_form(tipocita=tipocita)
        colores = tcitadao.get_lista_colores()
        return {'status': 200, 'form': form, 'horas': horas, 'colores': colores}

    def do_save(self, userid, tcitadao):
        form = self.get_request_json_body()
        ct_id = int(form['ct_id'])
        msg = 'Registrado exitósamente'
        if ct_id > 0:
            msg = 'Actualizado exitósamente'
            tcitadao.actualizar(form, user_edita=userid)
        else:
            tcitadao.guardar(form, user_crea=userid)
        return {'status': 200, 'msg': msg}
