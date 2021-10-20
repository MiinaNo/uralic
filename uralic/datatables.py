from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol, IdCol, DetailsRowLinkCol
from clld.web.datatables.value import Values
from clld.web.datatables.parameter import Parameters
from clld.web.util.htmllib import HTML
from clld.db.models import common
from clld.db.util import get_distinct_values

from uralic import models
from uralic import util


class Languages(datatables.Languages):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self, "Subfamily", model_col=models.Variety.subfamily),
            # Col(self, "Glottocode", model_col=models.Variety.glottocode),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            LinkToMapCol(self, 'm'),
        ]


class FeatureIDCol(LinkCol):
    # add the feature id column
    def get_attrs(self, item):
        return {'label': self.get_obj(item).id.split('-')[-1]}

    def get_obj(self, item):
        return item.valueset.parameter


class ExampleCol(Col):
    __kw__ = dict(bSearchable=False, bSortable=False)

    def format(self, item):
        if util.glossed_examples(item):
            return DetailsRowLinkCol(self.dt, '', button_text='Example').format(item)
        #return HTML.ul(*util.glossed_examples(item), class_='unstyled')
        return ''


class Datapoints(Values):
    # exclude the column of "Admixture coefficients"
    def base_query(self, query):
        q = Values.base_query(self, query)
        if self.parameter is None:
            return q.filter(common.Parameter.id != 'adm')
        return q

    # exclude the columns of details and source
    def col_defs(self):
        res = [c for c in Values.col_defs(self) if not c.name in ['d', 'source']]
        # print(IdCol(self, 'id').get_attrs())
        return res + [
            Col(self, 'description', sTitle='Comment'),
            ExampleCol(self, 'example'),
            FeatureIDCol(self, 'id', get_object=lambda i: i.valueset.parameter)]


class Params(Parameters):
    # exclude the column of "id"
    def base_query(self, query):
        return Parameters.base_query(self, query).filter(common.Parameter.id != 'adm')\
            .join(models.Feature.contribution)

    def col_defs(self):
        return [
            IdCol(self, 'id'),
            Col(self,
                'dataset',
                model_col=common.Contribution.id,
                choices=get_distinct_values(common.Contribution.id),
                get_object=lambda i: i.contribution),
            LinkCol(self, 'name'),
            Col(self, 'domain', model_col=models.Feature.category),
            DetailsRowLinkCol(self, '#', button_text='values'),
        ]


def includeme(config):
    """register custom datatables"""
    config.register_datatable('parameters', Params)
    config.register_datatable('languages', Languages)
    config.register_datatable('values', Datapoints)
