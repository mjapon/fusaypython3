from fusayrepo.logica.dao.base import BaseDao
from fusayrepo.logica.fusay.tfuser.tfuser_model import TFuserSec
from fusayrepo.logica.fusay.tseccion.tseccion_dao import TSeccionDao


class TFuserSecDao(BaseDao):

    @staticmethod
    def get_form(us_id):
        return {
            'fus_id': 0,
            'us_id': us_id,
            'sec_id': 0,
            'fus_main': False
        }

    def get_secciones_form(self, sec_id):
        secdao = TSeccionDao(self.dbsession)
        secciones = secdao.listar()
        for sec in secciones:
            sec['fus_main'] = sec['sec_id'] == sec_id
            sec['sec_marca'] = sec['sec_id'] == sec_id

        return secciones

    def crear(self, form):
        tfusersec = TFuserSec()
        tfusersec.us_id = form['us_id']
        tfusersec.sec_id = form['sec_id']
        tfusersec.fus_main = form['fus_main']

        self.dbsession.add(tfusersec)

    def create_from_list(self, us_id, secciones):
        current_secs = self.dbsession.query(TFuserSec).filter(TFuserSec.us_id == us_id).all()
        for fusec in current_secs:
            self.dbsession.delete(fusec)

        for sec in secciones:
            if sec['sec_marca']:
                self.crear({'us_id': us_id, 'sec_id': sec['sec_id'], 'fus_main': sec['fus_main']})

    def get_secciones_user(self, us_id):
        sql = """
        select fs.fus_id, fs.us_id, fs.sec_id, sec.sec_nombre, fs.fus_main from tfusersec fs
        join tseccion sec on fs.sec_id = sec.sec_id
         where us_id = {0}
        """.format(us_id)

        tupla_desc = ('fus_id', 'us_id', 'sec_id', 'sec_nombre', 'fus_main')
        return self.all(sql, tupla_desc)

    def get_secs_user_for_edit(self, us_id):
        sql = """
        select sec.sec_id, sec.sec_nombre, 
        case when coalesce(fs.sec_id, 0) > 0 then true else false end as sec_marca,
        coalesce (fs.fus_main,false) as fus_main
        from tseccion sec
        left join tfusersec fs on sec.sec_id = fs.sec_id and fs.us_id = {0}
        where sec.sec_estado = 1 order by sec.sec_nombre asc
        """.format(us_id)

        print('sql:')
        print(sql)

        tupla_desc = ('sec_id', 'sec_nombre', 'sec_marca', 'fus_main')

        return self.all(sql, tupla_desc)
