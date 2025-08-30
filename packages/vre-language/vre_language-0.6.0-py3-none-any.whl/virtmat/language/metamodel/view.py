"""module for data visualization"""
import numpy
import pandas
import seaborn
from matplotlib import pyplot
from virtmat.language.utilities.types import is_array_type, is_array, is_numeric, NC
from virtmat.language.utilities.errors import RuntimeTypeError, RuntimeValueError
from virtmat.language.utilities.errors import textxerror_wrap, raise_exception, error_handler
from virtmat.language.utilities.warnings import warnings, TextSUserWarning
from virtmat.language.utilities.units import get_units, get_df_units
from virtmat.language.utilities.units import convert_df_units, strip_units, ureg
from virtmat.language.utilities.arrays import get_nested_array
from virtmat.language.interpreter.workflow_executor import get_par_value
from virtmat.language.utilities.ase_viewers import display_amml_structure
from virtmat.language.utilities.ase_viewers import display_amml_trajectory
from virtmat.language.utilities.ase_viewers import display_vibration
from virtmat.language.utilities.ase_viewers import display_bs, display_eos, display_neb
from virtmat.language.utilities.ase_viewers import display_waterfall


def display_seaborn(obj, show=True):
    """Display numerical data on xy-plots using the seaborn package

      Args:
          obj (view object: instance of metamodel class View)

      The types of the values of obj.params attribute:
       * parameters for long-form data:
         tab (pandas.DataFrame): table with the data (dataframe index not used)
         x_name (str): the name of the column to use as x axis
         y_name (str): the name of the column to use as y axis
         units (series): string series owith name 'units' and of length the
           number of columns in tab

       * parameters for wide-form data:
         values: series of 1D arrays or a 2D array of scalar type
           dim(values) must be either (len(index), len(columns))
                                   or (len(columns), len(index))
         index: series or 1D array of scalar type
         columns: series, 1D array or tuple of hashable types

       * parameters for simple xy data:
         values: series or 1D array of scalar type
         index: series or 1D array of scalar type

      Raises:
          RuntimeTypeError: if the types of the parameters are incorrect

    """
    sbfunc = getattr(seaborn, obj.mode)
    assert obj.params[0].type_ is not None
    if issubclass(obj.params[0].type_, pandas.DataFrame):
        tab = obj.params[0].value
        x_name = obj.params[1].value
        y_name = obj.params[2].value
        try:
            assert isinstance(tab, pandas.DataFrame)
            assert isinstance(x_name, str)
            assert isinstance(y_name, str)
        except AssertionError as err:
            raise_exception(obj, RuntimeTypeError, str(err))
        if x_name not in tab.columns:
            msg = f'could not find x-axis data "{x_name}" in table'
            raise_exception(obj.params[1], RuntimeValueError, msg)
        if y_name not in tab.columns:
            msg = f'could not find y-axis data "{y_name}" in table'
            raise_exception(obj.params[2], RuntimeValueError, msg)
        if len(obj.params) > 3:
            units = obj.params[3].value
            if not isinstance(units, pandas.Series) or units.name != 'units':
                msg = 'parameter must be series with name "units"'
                raise_exception(obj.params[3], RuntimeTypeError, msg)
            if len(units) != len(tab.columns):
                msg = f'length of units series must be {len(tab.columns)}'
                raise_exception(obj.params[3], RuntimeValueError, msg)
            tab = convert_df_units(tab, units)
        units = get_df_units(tab)
        _, axes = pyplot.subplots()
        x_units = units[tab.columns.get_loc(x_name)]
        y_units = units[tab.columns.get_loc(y_name)]
        axes.set_xlabel(f'{x_name} [{x_units}]')
        axes.set_ylabel(f'{y_name} [{y_units}]')
        # axes.xaxis.set_units(x_units) #  smarter but does not work
        # axes.yaxis.set_units(y_units) #  smarter but does not work
        _ = sbfunc(tab.map(strip_units), x=x_name, y=y_name, ax=axes)
    elif (issubclass(obj.params[0].type_, pandas.Series) or
          is_array_type(obj.params[0].type_)):
        values = obj.params[0].value
        index = obj.params[1].value
        x_units = get_units(index)
        y_units = get_units(values)

        if len(obj.params) > 2:
            try:
                columns = obj.params[2].value
                if isinstance(columns, (numpy.ndarray, pandas.Series)):
                    assert len(columns.shape) == 1
                else:
                    assert isinstance(columns, (tuple, list, set))
                    columns = pandas.Series(columns)

                if isinstance(values, pandas.Series):
                    y_name = values.name
                    values = get_nested_array(values.values)
                else:
                    assert is_array(values)
                    y_name = ''

                if isinstance(index, pandas.Series):
                    x_name = index.name
                    index = index.map(strip_units)
                    if len(index) == 1 and is_array(index[0]):
                        index = index[0]
                    else:
                        index = index.values
                else:
                    assert isinstance(index, (numpy.ndarray, ureg.Quantity))
                    if isinstance(index, ureg.Quantity):
                        assert isinstance(index.magnitude, numpy.ndarray)
                    if len(index.shape) > 1:
                        assert len(index.shape) == 2
                        assert index.shape[0] == 1
                        index = index[0]
                    x_name = ''

                if columns.shape[0] != values.shape[1]:
                    assert index.shape[0] == values.shape[1]
                    assert columns.shape[0] == values.shape[0]
                    values = values.transpose()
                else:
                    assert index.shape[0] == values.shape[0]
                    assert columns.shape[0] == values.shape[1]
            except AssertionError as err:
                raise_exception(obj, RuntimeTypeError, str(err))

            if is_numeric(columns):
                columns = [f'{c.magnitude} [{c.units}]' for c in columns]

            df = pandas.DataFrame(values, index, columns=columns)
            _, axes = pyplot.subplots()
            axes.set_xlabel(f'{x_name} [{x_units}]')
            axes.set_ylabel(f'{y_name} [{y_units}]')
            _ = sbfunc(df.map(strip_units), ax=axes)
        else:
            if is_array(index):
                index = pandas.Series(index, name='x')
            if is_array(values):
                values = pandas.Series(values, name='y')
            df = pandas.concat([index, values], axis='columns')
            _, axes = pyplot.subplots()
            axes.set_xlabel(f'{index.name} [{x_units}]')
            axes.set_ylabel(f'{values.name} [{y_units}]')
            _ = sbfunc(df.map(strip_units), x=index.name, y=values.name, ax=axes)
    else:
        types = [p.type_ for p in obj.params]
        msg = f'unknown types of view params: {types}'
        raise_exception(obj, RuntimeTypeError, msg)
    if show:
        pyplot.show()


@error_handler
@textxerror_wrap
def display(self, show=True):
    """define display() method in View metamodel class"""
    if any(get_par_value(par) is NC for par in self.params):
        par = next(p for p in self.params if get_par_value(p) is NC)
        msg = 'parameter value is not computed yet'
        warnings.warn(TextSUserWarning(msg, obj=par))
        return
    if self.mode in ('lineplot', 'scatterplot'):
        display_seaborn(self, show=show)
    elif self.mode == 'bs':
        display_bs(self, show=show)
    elif self.mode == 'eos':
        display_eos(self, show=show)
    elif self.mode == 'neb':
        display_neb(self, show=show)
    elif self.mode == 'vibration':
        display_vibration(self, show=show)
    elif self.mode == 'trajectory':
        display_amml_trajectory(self, show=show)
    elif self.mode == 'waterfall':
        display_waterfall(self, show=show)
    else:
        assert self.mode == 'structure'
        display_amml_structure(self, show=show)
    if show:
        pyplot.close()


def add_display(metamodel):
    """add display method to the View metamodel class"""
    setattr(metamodel['View'], 'display', display)
