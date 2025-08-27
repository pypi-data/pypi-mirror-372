import ast
from typing import Any

from ._exceptions import (
   InvalidArgumentError, 
   MissingLabelError,
   SYMBOL,
) 


DEBUG_TYPE_ERROR = (
   "'debug' must be a boolean, a single string, "
   "a list or tuple of strings."
)
INVALID_LABEL = "Label cannot be empty or blank."
INDEX_ERROR = (
   "'index' must be an integer or a tuple containing only integers."
)
VAR_TYPE_ERROR = (
   "The argument must be a string, multiple strings, "
   "or a list/tuple of strings."
)


def _try_search_var(
      self, node: ast.Name | ast.Attribute, 
      err_check = False, get_full_name: bool = False,
) -> tuple[str, Any] | tuple[str, Any, bool] | str:
   if isinstance(node, ast.Name):
      try:
         ret_value = self._frame.f_locals[node.id]
      except KeyError:
         try:
            ret_value = self._frame.f_globals[node.id]
         except KeyError:
            raise NameError(f"'{node.id}' is not defined.")

      var_name = node.id 

      if get_full_name:
         return (var_name, var_name)  
   else:
      try:
         ret_value = self._frame.f_locals[node.value.id]
         var_name = node.value.id
      except KeyError:
         ret_value = self._frame.f_globals[node.value.id]
         var_name = node.value.id
      except AttributeError:
         if err_check:
            raise InvalidArgumentError(
               "Provided value is not a variable or is not supported."
            )

         (attr_id, attr_full_name) = _get_attr_fullname(node)

         try:
            ret_value = self._frame.f_locals[attr_id]
         except KeyError:
            ret_value = self._frame.f_globals[attr_id]
            
         var_name = attr_id

         if get_full_name:
            return (var_name, attr_full_name)
         
      if get_full_name:
         return (var_name, f"{var_name}.{node.attr}")
      if err_check:
         return var_name
      
   return (var_name, ret_value)
   

def _get_attr_fullname(node: ast.Attribute) -> tuple[str, str]:
   name = []

   while isinstance(node, ast.Attribute):
      name.append(node.attr)
      node = node.value

   if isinstance(node, ast.Name):
      name.append(node.id)
      name.reverse()
   else:
      raise TypeError(
         "The attribute structure used in 'cond' is not supported."
      )

   return (name[0], ".".join(name))

def _get_nested_value(self, attr_name: str) -> str | int:
   parts = attr_name.split(".")

   try:
      ref = self._frame.f_locals[parts[0]]
   except KeyError:
      try:
         ref = self._frame.f_globals[parts[0]]
      except KeyError:
         raise InvalidArgumentError(
            f"'{attr_name}' is not defined in the current scope."
         )
      
   for attr in parts[1:]:
      ref = getattr(ref, attr)
   return ref

def _ensure_label_exists(self, label: Any, unpack: bool = False) -> None:
    if unpack:
      if isinstance(label[0], (list, tuple)):
         label = label[0]
      elif not isinstance(label[0], str):
         raise TypeError("Label must be a string or a sequence of strings.")

    if isinstance(label, str):
       label = [label]

    for v in label:
      try:
         self._new_values[v]
      except KeyError:
         raise MissingLabelError(v)
      
def _ensure_debug_type(self) -> None:
   if not isinstance(self.debug, (str, list, tuple)):
      raise TypeError(DEBUG_TYPE_ERROR)
   if isinstance(self.debug, str):
      self.debug = [self.debug]
   elif any(v for v in self.debug if not isinstance(v, str)):
      raise TypeError(DEBUG_TYPE_ERROR)
   
   for v in self.debug:
      if v not in self._new_values.keys():
         raise MissingLabelError(v)

def _compare_value_counts(
      self, label: str | list[str], 
      needed_indexes_count: int | tuple[int, ...] | range, 
) -> None:
   # Note: `len(total_values)` is always one more than the max index

   if isinstance(needed_indexes_count, int):
      needed_indexes_count = (needed_indexes_count,)
   elif isinstance(needed_indexes_count, range):
      needed_indexes_count = tuple(needed_indexes_count)

   if isinstance(label, str):
      label = [label]
   for index in needed_indexes_count:
      for v in label:
         if len(self._new_values[v]) < index + 1:
            raise IndexError(
               f"Please set the new value for '{v}' at index {index}."
            ) 
         

def _count_symbol(label: str) -> int:
   count = 0

   # count only prefix symbols
   for symbol in label:
      if symbol == SYMBOL:
         count += 1
         continue
      return count
   
   
def _ensure_index_type(index: Any, allow_tuple: bool = False) -> None:
   if index is None:
      return
   
   if not allow_tuple:
      if isinstance(index, bool) or not isinstance(index, int):
         raise TypeError("'index' must be an integer.")
   elif allow_tuple:
      if isinstance(index, bool) or not isinstance(index, (int, tuple, range)):
         raise TypeError(INDEX_ERROR)
      
   if isinstance(index, (tuple, range)):
      if isinstance(index, range):
         index = tuple(index)

      for i in index:
         if not isinstance(i, int):
            raise TypeError(IndexError)     
    

def _ensure_label_type(
      label: Any, allow_dict: bool = False, allow_seq: bool = True, 
      unpack: bool = False,
) -> None:
   if allow_seq:
      err_msg = "Label must be a string or a sequence of strings."
   else:
      err_msg = "Label must be a string."

   if unpack:
      if isinstance(label[0], (list, tuple)):
         label = label[0]
      elif not isinstance(label[0], str):
         raise TypeError(err_msg)

   if not allow_dict and isinstance(label, dict):
      raise TypeError(
         "dict type is not allowed for 'label'."
      )
   elif isinstance(label, (str, tuple, list)):
      if isinstance(label, str):
         if label == "" or " " in label:
            raise InvalidArgumentError(INVALID_LABEL)
         label = [label]

      for v in label:
         if not isinstance(v, str):
            raise TypeError(err_msg)
         elif v == "" or " " in v:
            raise InvalidArgumentError(INVALID_LABEL)
   else:
      raise TypeError(err_msg)
   

def _ensure_after_type(after: Any) -> None:
   if after is None:
      return
   elif not isinstance(after, (int, float)):
      raise TypeError("'after' must be int or float.")
   elif after < 0:
      raise InvalidArgumentError("'after' must be a non-negative number.")
   

def _ensure_var_type(var: Any) -> tuple[str, ...] | list[str]:
   if not isinstance(var[0], (list, tuple, str)):
      raise TypeError(VAR_TYPE_ERROR)
   
   if isinstance(var[0], (list, tuple)):
      var = var[0]

   for v in var:
      if not isinstance(v, str):
         raise TypeError(VAR_TYPE_ERROR)
      elif "." in v and v.count(".") != 1:
         raise ("Please pass variables or class attributes.")
        
   return var
      

def _normalize_arg_types(
      label: Any, value: Any | None, index: Any = None,
) -> dict[str, Any]:
   if index is not None:
      _ensure_index_type(index)
      
   # single label
   if isinstance(label, str):    
      if label == "" or " " in label:
         raise InvalidArgumentError(INVALID_LABEL)  
      elif isinstance(value, (list, tuple)):          
        return {label: value}    
      else:        
         return {label: value}   
   elif isinstance(label, dict):
      # multiple labels
      if len(label) == 0:
         raise InvalidArgumentError(
            "Please provide both a key and a value for the dictionary."
         )   
      elif value is None:
         for key in label.keys():
            if not isinstance(key, str):
               raise TypeError("All labels must be strings.")
            elif key == "" or " " in key:
               raise InvalidArgumentError(INVALID_LABEL)    
         return label
      
      raise InvalidArgumentError(
         "All required values must be included "
         "in the dictionary provided to 'label' "
         "Do not pass them as separate arguments."
      )
   else:
      raise TypeError("'label' must be a string or a dictionary.")
   

def _ensure_allowed_cond(scope: dict[str, Any], nodes: list[ast.AST]) -> None:
   cmp = (ast.Compare, ast.BoolOp, ast.UnaryOp)

   allowed = (
    # Expr & names
    ast.Expression, ast.Name, ast.Attribute, ast.Subscript, ast.Slice,
    # Literals & containers
    ast.Constant, ast.Tuple, ast.List, ast.Set, ast.Dict,
    # Comparisons
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Is, ast.IsNot, ast.In, ast.NotIn,
    # Boolean ops
    ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    # Binary ops
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
    ast.FloorDiv, ast.MatMult, ast.BitAnd, ast.BitOr, ast.BitXor,
    ast.LShift, ast.RShift,
    # Unary ops
    ast.UAdd, ast.USub, ast.Invert,
    # Context
    ast.Load,
   )

   if all(isinstance(n, allowed) for n in nodes):
      if len(nodes) == 2 and any(isinstance(n, ast.Constant) for n in nodes):
         if isinstance(nodes[1].value, bool):
            return
      elif len(nodes) == 3 and len(scope) == 1:
         if isinstance(next(iter(scope.values())), bool):
            return
      if any(isinstance(n, cmp) for n in nodes):
            return
   
   raise InvalidArgumentError(
      "Only comparison expressions (e.g. x > 10, a == b) are allowed."
   )