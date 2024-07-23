# coding: utf-8
from fusayrepo.logica.dao.base import BaseDao


class TUserEmailDao(BaseDao):

    def autenticar(self, email, clave):
        sql = ("select count(*) as cuenta from tuseremail where "
               "ue_email = :user and ue_password = :passw and ue_status = true")
        result = self.first_raw(sql, user=email, passw=clave)
        return result[0] > 0 if result is not None else False

    def autenticarEmail(self, email):
        sql = ("select count(*) as cuenta from tuseremail where "
               "ue_email = :user and ue_status = true")
        result = self.first_raw(sql, user=email)
        return result[0] > 0 if result is not None else False

    def get_user_info(self, email):
        sql = "select ue_email, ue_emplist from tuseremail where ue_email = :email"
        result = self.first_raw(sql, email=email)
        tupla_desc = ('usuario', 'empresas')
        return self.tupla_to_json(result, tupla_desc)

    def get_emp_schemas(self, empcods):
        sql = "select emp_id, emp_esquema, emp_nombrecomercial from public.tempresa where emp_id in (:empcods)"
        result = self.all_raw(sql, empcods=empcods)
        tupla_desc = ('emp_id', 'emp_esquema', 'emp_nombrecomercial')
        return self.make_json_list(result, tupla_desc)
