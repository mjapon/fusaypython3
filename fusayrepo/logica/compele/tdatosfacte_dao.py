from fusayrepo.logica.dao.base import BaseDao


class TDatosFacteDao(BaseDao):

    def find_by_emp_codigo(self, emp_ruc):
        sql = """
        select emp.emp_codigo, df.df_pathdigital_sign, df.df_passdigital_sign from
        comprobantes.tempresa emp join comprobantes.tdatosfacte df on emp.emp_codigo = df.emp_codigo
        where emp.emp_ruc = :ruc 
        """

        result = self.first_raw(sql, ruc=emp_ruc)
        tupla_desc = ('emp_codigo', 'df_pathdigital_sign', 'df_passdigital_sign')
        return self.tupla_to_json(result, tupladesc=tupla_desc)
