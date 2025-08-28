# coding=utf-8
from typing import Any
from collections.abc import Callable

from ut_obj.str import Str
from ut_obj.strdate import StrDate

TyArr = list[Any]
TyDic = dict[Any, Any]
TyCall = Callable[..., Any]
TyDoEq = dict[str, Any]
TyStr = str

TnDic = None | TyDic
TnStr = None | TyStr


class DoEq:
    """ Manage Commandline Arguments
    """
    @staticmethod
    def _set_sh_prof(d_eq: TyDoEq, sh_prof: TyCall | Any) -> None:
        """ set current pacmod dictionary
        """
        if callable(sh_prof):
            d_eq['sh_prof'] = sh_prof()
        else:
            d_eq['sh_prof'] = sh_prof

    @classmethod
    def sh_value_by_key_type(cls, d_eq: TyDoEq, d_valid_parms: TnDic) -> TyDoEq:
        # Log.debug("key", key)
        # Log.debug("value", value)
        if not d_valid_parms:
            return d_eq
        d_eq_new = {}
        for key, value in d_eq.items():
            _type: TnStr = d_valid_parms.get(key)
            if _type is None:
                msg = (f"Wrong parameter: {key}; "
                       f"valid parameters are: {d_valid_parms}")
                raise Exception(msg)
            match _type:
                case 'int':
                    value = int(value)
                case 'bool':
                    value = Str.sh_boolean(value)
                case 'dict':
                    value = Str.sh_dic(value)
                case 'list':
                    value = Str.sh_arr(value)
                case '%Y-%m-%d':
                    value = StrDate.sh(value, _type)
                case '_':
                    match _type[0]:
                        case '[', '{':
                            _obj = Str.sh_dic(_type)
                            if value not in _obj:
                                msg = (f"parameter={key} value={value} is invalid; "
                                       f"valid values are={_obj}")
                                raise Exception(msg)
            d_eq_new[key] = value
        return d_eq_new

    @classmethod
    def verify(cls, d_eq: TyDoEq, d_parms: TnDic) -> TyDoEq:
        if d_parms is None:
            return d_eq
        if 'cmd' in d_eq:
            _d_valid_parms = d_parms
            _cmd = d_eq['cmd']
            _valid_commands = list(d_parms.keys())
            if _cmd not in _valid_commands:
                msg = (f"Wrong command: {_cmd}; "
                       f"valid commands are: {_valid_commands}")
                raise Exception(msg)
            _d_valid_parms = d_parms[_cmd]
        else:
            _d_valid_parms = d_parms
        if _d_valid_parms is None:
            return d_eq

        d_eq_new: TyDoEq = cls.sh_value_by_key_type(d_eq, _d_valid_parms)
        return d_eq_new

    @classmethod
    def sh_d_eq(cls, d_equ: TyDoEq, **kwargs) -> TyDic:
        """ show equates dictionary
        """
        _d_parms: TnDic = kwargs.get('d_parms')
        _prof = kwargs.get('sh_prof')
        _d_eq: TyDic = DoEq.verify(d_equ, _d_parms)
        DoEq._set_sh_prof(_d_eq, _prof)
        return _d_eq
