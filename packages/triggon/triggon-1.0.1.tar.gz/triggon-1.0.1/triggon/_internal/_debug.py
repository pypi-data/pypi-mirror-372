import os
from types import FunctionType
from typing import Any

from ._err_handler import SYMBOL, _count_symbol
from ._sentinel import _NO_VALUE
from ._var_update import _get_delay_index, _is_delayed_func

LOG_DEBUG = "【Debug】 [File] {file} [Line] {lineno} [Function] {func} "

LOG_FLAG = LOG_DEBUG + "[State] Label '{label}' is {state}"
LOG_FLAG_AFTER = LOG_DEBUG + "[State] Label '{label}' will be {state} after {timer}s"

LOG_TRIG = LOG_DEBUG + "[Label] {label} [Action] {action}"

LOG_VALUE = (
  LOG_DEBUG 
  + "[Label] {label} (index {num}) [Value] {value}"
)

LOG_VALUE_MULT = (
  LOG_DEBUG 
  + "[Label] {label} (index {num}) [Value] {value}"
)

LOG_VAR = (
  LOG_DEBUG 
  + "[Label] {label} (index {num}) [Variable] {var} [Value] {value}"
)


def _get_debug_info(self) -> tuple[str, int, str]:
   func_name = self._frame.f_code.co_name
   lineno = self._frame.f_lineno
   file_name = self._frame.f_code.co_filename
   return (file_name, lineno, func_name)

def _get_delay_info(self, label: str, index: int) -> tuple[str, int, str]:
   func_name = self._delay_info[label][index][3]
   lineno = self._delay_info[label][index][2]
   file_name = self._delay_info[label][index][1]
   return (file_name, lineno, func_name)

def _get_var_info(
        self, label: str, index: int, inner_index: int = None,
) -> str:
   if inner_index is None:
       var_refs = self._var_refs[label][index]
       if var_refs is None:
          return var_refs
   else:
       check_refs = self._var_refs[label][index]
       if check_refs is None:
          return check_refs
       var_refs = check_refs[inner_index]
       
   return var_refs[2]

# for `set_trigger()` and `revert()`

def _print_flag_debug(
      self, labels: list[str], state: str, after: int | float,
      index: int = None, delay: bool = False, flags: list[bool] = None,
) -> None:
    if not delay:
       (file, lineno, func) = self._get_debug_info()
    else:
       (file, lineno, func) = self._get_delay_info(labels[0], index)

    f_name = os.path.basename(file)

    for i, label in enumerate(labels):
      if flags is not None and flags[i]:
         continue
      if after is not None:
         print(
            LOG_FLAG_AFTER.format(
               file=f_name, lineno=lineno, 
               func=func, label=label, 
               state=state, timer=after,
            )
         )
      else:
         print(
            LOG_FLAG.format(
               file=f_name, lineno=lineno, 
               func=func, label=label, state=state,
            )
         )

# for `switch_lit()`

def _print_val_debug(
      self, 
      label: str | tuple[str, ...], index: int | tuple[int, ...], 
      before: Any, after: Any | object,
) -> None:
      (file, lineno, func) = self._get_debug_info()
      f_name = os.path.basename(file)

      if _is_delayed_func(before):
         before = _get_func_name(before)
      if _is_delayed_func(after):
         after = _get_func_name(after)

      if isinstance(label, str):
         log_fmt = LOG_VALUE
      else:
         log_fmt = LOG_VALUE_MULT

      if after is _NO_VALUE:
         print(
            log_fmt.format(
               file=f_name, lineno=lineno, 
               func=func, label=label, num=index, 
               value=repr(before),
            )
         )
      else:
         print(
            log_fmt.format(
               file=f_name, lineno=lineno, 
               func=func, label=label, num=index, 
               value=f"{repr(before)} → {repr(after)}",
            )
         )

      self._clear_frame()

# for `switch_var()`

def _print_var_debug(
      self, label: str, index: int, inner_index: int, new_value: Any, 
      delay: bool, prev_value: Any, to_org: bool = False,
) -> None:
   if not delay:
       (file, lineno, func) = self._get_debug_info()
   else:
       i = _get_delay_index(to_org)
       (file, lineno, func) = self._get_delay_info(label, i)

   f_name = os.path.basename(file)

   # `prev_value` is the original value of this variable
   var_name = self._get_var_info(label, index, inner_index)

   if _is_delayed_func(prev_value):
      prev_value = _get_func_name(prev_value)
   if _is_delayed_func(new_value):
      new_value = _get_func_name(new_value)

   if new_value is _NO_VALUE:
         value = repr(prev_value)
   elif type(prev_value) != type(new_value) or prev_value != new_value:
         value = f"{repr(prev_value)} → {repr(new_value)}"
   else:
         new = self._new_values[label][index]
         value = f"{repr(new)} → {repr(new_value)}"

   print(
      LOG_VAR.format(
         file=f_name, lineno=lineno, 
         func=func, label=label, num=index, 
         var=var_name, value=value,
      )
   )

# for `trigger_return()` and `trigger_func()`

def _print_trig_debug(
      self, label: str, action: str, target_func: FunctionType = None,
) -> None:
   (file, lineno, func) = self._get_debug_info()
   f_name = os.path.basename(file)

   if action == "triggered":
      trig_func = _get_func_name(target_func)
      action = f"{action} {trig_func}"

   print(
      LOG_TRIG.format(
         file=f_name, lineno=lineno, 
         func=func, label=label, action=action,
      )
   )

   self._clear_frame()

def _get_marks(
        self, label: str | list[str] | tuple[str, ...] = None, 
        index: int = None, org: Any = _NO_VALUE, new: Any = _NO_VALUE,
        init: bool = False, strip: bool = False,
) -> None:
   if self.debug is False:
      return

   if init:
      self._get_target_frame("switch_lit")

      org_label = f"_org_{self._file_name}_{self._lineno}"
      new_label = f"_new_{self._file_name}_{self._lineno}"

      if getattr(type(self).switch_lit, org_label, None) is None:
         setattr(type(self).switch_lit, org_label, True) # Set a bool
         setattr(type(self).switch_lit, new_label, None) # Set a label 
      return
   
   org_label = f"_org_{self._file_name}_{self._lineno}"
   new_label = f"_new_{self._file_name}_{self._lineno}"

   if index is None:
      if isinstance(label, str):
         index = _count_symbol(label)
      else:
         index = tuple(_count_symbol(v) for v in label) # Only when org value

   if strip:
      if isinstance(label, str):
         label = label.lstrip(SYMBOL)
      else:
         label = tuple(v.lstrip(SYMBOL) for v in label) # Only when org value

   if new is _NO_VALUE:
       # To org value
       setattr(type(self).switch_lit, org_label, True)

       if getattr(type(self).switch_lit, new_label, None) is None:
         prev_value = org
         new_value = _NO_VALUE
       else:
         prev_label = getattr(type(self).switch_lit, new_label, None)

         if isinstance(index, int):
            i = index
         else:
            label_idx = label.index(prev_label)
            i = index[label_idx]
         prev_value = self._new_values[prev_label][i]
         new_value = org

       setattr(type(self).switch_lit, new_label, None)
   else:
       # To new value
       if not getattr(type(self).switch_lit, org_label, False):
         prev_label = getattr(type(self).switch_lit, new_label, None)
         if prev_label is None or new == self._new_values[prev_label][index]:
            prev_value = new
            new_value = _NO_VALUE 
         else:
            prev_value = self._new_values[prev_label][index]
            new_value = new 
       else:
         prev_value = org
         new_value = new

       setattr(type(self).switch_lit, new_label, label)
       setattr(type(self).switch_lit, org_label, False)

   target_label = self._check_target_labels(label)
   if not target_label:
      return

   self._print_val_debug(label, index, prev_value, new_value)

def _debug_trigger(
      self, labels: list[str], flags: list[bool],
      after: int | float | None, delay: bool = False,
) -> None:
   if not self.debug:
       return
   
   target_labels = self._check_target_labels(labels)
   if not target_labels:
      return

   if delay:
      self._print_flag_debug(
         target_labels, "active", after, 0, flags=flags, delay=True,
      )
   else:
      self._get_target_frame("set_trigger")
      self._print_flag_debug(target_labels, "active", after, flags=flags)

def _debug_revert(
      self, labels: list[str], after: int | float | None, disable: bool,
      delay: bool = False,
) -> None:
    if not self.debug:
        return

    target_labels = self._check_target_labels(labels)
    if not target_labels:
        return

    if disable:
        state = "disable"
    else:
        state = "inactive"

    if delay:
      self._print_flag_debug(
         target_labels, state, after, 1, delay=True,
      )
    else:
       self._get_target_frame("revert")
       self._print_flag_debug(target_labels, state, after)

def _debug_update(
      self, label: str, index: int, inner_index: int | None, 
      update_value: Any, to_org: bool = False, 
      prev_value: Any = _NO_VALUE,
) -> None:
    if not self.debug:
        return

    target_label = self._check_target_labels(label)
    if not target_label:
       return

    i = _get_delay_index(to_org)
    if self._delay_info[label][i] is None:
      delay = False
    else:
      delay = True

    self._print_var_debug(
       label, index, inner_index, update_value, 
       delay, prev_value, to_org,
    )

def _debug_trig_return(self, label: str) -> None:
    if not self.debug:
        return
    self._get_target_frame("trigger_return")
    self._print_trig_debug(label, "early return")

def _debug_trig_func(self, label: str, func: FunctionType) -> None:
   if not self.debug:
      return
   self._get_target_frame("trigger_func")
   self._print_trig_debug(label, "triggered", func) 

def _check_target_labels(
      self, labels: str | list[str] | tuple[str, ...],
) -> list[str] | None:
   if isinstance(self.debug, bool):
      return labels
   elif isinstance(labels, str):
      labels = [labels]

   return [v for v in labels if v in self.debug]

def _check_var_refs(
      self, left: type | str, right: str = None, is_glob: bool = False,
) -> bool:
   for refs in self._var_refs.values():
      for ref in refs:
         if ref is None:
            continue
         if isinstance(ref, list):
            for v in ref:
               if right is None:
                  if (
                     len(v) == 3 
                     and v[0] == self._file_name and v[2] == left
                  ):
                     return True
               else:
                  if len(v) == 4:
                     if is_glob:
                        cmp_left = v[3].__class__.__name__
                     else:
                        cmp_left = v[3]
                     if v[2] == right and cmp_left == left:


                        return True
         else:
            if right is None:
               if (
                  len(ref) == 3 
                  and ref[0] == self._file_name and ref[2] == left
               ):
                  return True
            else:
               if len(ref) == 4:
                  if len(v) == 4:
                     if is_glob:
                        cmp_left = ref[3].__class__.__name__
                     else:
                        cmp_left = ref[3]
                     if ref[2] == right and cmp_left == left:
                        return True
                        
   return False


def _get_func_name(func: FunctionType) -> str:
   name = getattr(func, "_trigfunc_name", None)
   if name is None:
      return f"{func}()"
   
   args = getattr(func, "_trigfunc_args", None)
   kwargs = getattr(func, "_trigfunc_kwargs", None)

   contents = []

   if args:
      for arg in args:
         contents.append(repr(arg))
   if kwargs:
      for k, v in kwargs.items():
         fmt = f"{repr(k)}={repr(v)}"
         contents.append(fmt)
      
   if not contents:
      return f"{name}()"
   elif len(contents) == 1:
      return f"{name}({contents[0]})"
   return f"{name}{tuple(contents)}"