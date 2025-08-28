from bisect import bisect_left, bisect_right
from typing import Union
from PyQt6.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt6.QtWidgets import QApplication

from elftools.dwarf.die import DIE
from elftools.dwarf.compileunit import CompileUnit

from .fx import bold_font, blue_brush
from .dwarfutil import DIE_has_name, DIE_name, has_code_location, safe_DIE_name, top_die_file_name
from .dwarfone import DIEV1


def cu_sort_key(cu):
    return top_die_file_name(cu.get_top_DIE()).lower()

def die_sort_key(die):
    name = safe_DIE_name(die)
    tag = '%X' % die.tag if isinstance(die.tag, int) else die.tag
    return (tag, name, die.offset)

#------------------------------------------------
# CU tree formatter
#------------------------------------------------    

# Some additional data for every DIE
def decorate_die(die, i):
    die._i = i
    die._children = None
    return die

def load_children(parent_die: Union[DIE, DIEV1] , sort: bool): #(parent_die: Union[DIE, DIEV1] , sort: bool):
    # Load and cache child DIEs in the parent DIE, if necessary
    # Assumes the check if the DIE has children has been already performed
    if not hasattr(parent_die, "_children") or parent_die._children is None:
        # TODO: wait cursor here.
        try:
            parent_die._children = [decorate_die(die, i) for (i, die) in enumerate(parent_die.iter_children())]
            if sort:
                parent_die._children.sort(key = die_sort_key)
                for (i, die) in enumerate(parent_die._children):
                    die._i = i
        except KeyError as exc:
            # Catching #1516
            from .__main__ import version
            from .crash import report_crash
            from inspect import currentframe
            tb = exc.__traceback__
            ctxt = dict()
            try:
                cu = parent_die.cu
                ctxt['cu_offset'] = cu.cu_offset
                ctxt['dwarf_config'] = cu.dwarfinfo.config
                abbrev_codes = set(d.abbrev_code for d in cu._dielist if not d.is_null())
                at = cu.get_abbrev_table()
                format_attr_in_abbrev = lambda a: (a.name, a.form, a.value) if a.value is not None else (a.name, a.form)
                format_abbr = lambda ab: (ab.decl.tag, ab._has_children, tuple(format_attr_in_abbrev(a) for a in ab.decl.attr_spec))
                ctxt['abbrevs'] = {c: format_abbr(at.get_abbrev(c)) for c in abbrev_codes}
                stm = cu.dwarfinfo.debug_info_sec.stream
                crash_pos = ctxt['crash_pos'] = stm.tell()
                slice = stm.getbuffer()[cu.cu_offset:crash_pos+1]
                ctxt['cu_in_info'] =  ' '.join("%02x" % b for b in slice)
            except Exception:
                pass
            report_crash(exc, tb, version, currentframe(), ctxt)

            QApplication.instance().win.show_warning("This executable file is corrupt or incompatible with the current version of DWARF Explorer. Please consider creating a new issue at https://github.com/sevaa/dwex/, and share this file with the tech support.")
            parent_die._children = []

class DWARFTreeModel(QAbstractItemModel):
    def __init__(self, di, prefix, sortcus, sortdies):
        QAbstractItemModel.__init__(self)
        self.prefix = prefix
        self.top_dies = [decorate_die(CU.get_top_DIE(), i) for (i, CU) in enumerate(di._CUs)]
        self.highlight_condition = None
        self.sortcus = sortcus
        self.sortdies = sortdies

    # Qt callbacks. QTreeView supports progressive loading, as long as you feed it the "item has children" bit in advance

    def index(self, row, col, parent):
        if parent.isValid():
            parent_die = parent.internalPointer()
            # print("child of %s" % parent_die.tag)
            load_children(parent_die, self.sortdies)
            return self.createIndex(row, col, parent_die._children[row])
        else:
            return self.createIndex(row, col, self.top_dies[row])
        return QModelIndex()

    def flags(self, index):
        f = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if index.isValid() and not index.internalPointer().has_children:
            f = f | Qt.ItemFlag.ItemNeverHasChildren
        return f

    def hasChildren(self, index):
        return not index.isValid() or index.internalPointer().has_children

    def rowCount(self, parent):
        if parent.isValid():
            parent_die = parent.internalPointer()
            # print('rcount of %s' % parent_die.tag)
            if not parent_die.has_children: # Legitimately nothing
                return 0
            else:
                load_children(parent_die, self.sortdies)
                return len(parent_die._children)
        else:
            return len(self.top_dies)

    def columnCount(self, parent):
        return 1

    def parent(self, index):
        if index.isValid():
            parent = index.internalPointer().get_parent()
            if parent:
                return self.createIndex(parent._i, 0, parent)
        return QModelIndex()

    def data(self, index, role):
        die = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if die.tag == 'DW_TAG_compile_unit' or die.tag == 'DW_TAG_partial_unit': # CU/top die: return file name
                return top_die_file_name(die)
            else: # Return tag, with name if possible
                if isinstance(die.tag, int): # Happens with user tags, #1472
                    s = ('DW_TAG_user_%X' if self.prefix else 'user_%X') % die.tag
                else:
                    s = die.tag if self.prefix or not str(die.tag).startswith('DW_TAG_') else die.tag[7:]
                if DIE_has_name(die):
                    s += ": " + DIE_name(die)
                return s
        elif role == Qt.ItemDataRole.ToolTipRole:
            if die.tag == 'DW_TAG_compile_unit' or die.tag == 'DW_TAG_partial_unit':
                return safe_DIE_name(die, None)
        elif role == Qt.ItemDataRole.ForegroundRole and self.is_highlighted(die):
            return blue_brush
        elif role == Qt.ItemDataRole.FontRole and self.is_highlighted(die):
            return bold_font()

    # The rest is not Qt callbacks

    def is_highlighted(self, die):
        if not self.highlight_condition:
            return False
        return next((True for v in self.highlight_condition.values() if v(die)), False)

    def add_highlight(self, key, condition):
        if not self.highlight_condition:
            self.highlight_condition = {key:condition}
        else:
            self.highlight_condition[key] = condition
        self.dataChanged.emit(self.createIndex(0, 0, self.top_dies[0]), self.createIndex(len(self.top_dies)-1, 0, self.top_dies[-1]), (Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.FontRole))

    def remove_highlight(self, key):
        del self.highlight_condition[key]
        self.dataChanged.emit(self.createIndex(0, 0, self.top_dies[0]), self.createIndex(len(self.top_dies)-1, 0, self.top_dies[-1]), (Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.FontRole))

    def clear_highlight(self):
        self.highlight_condition = None
        if len(self.top_dies):
            self.dataChanged.emit(self.createIndex(0, 0, self.top_dies[0]), self.createIndex(len(self.top_dies)-1, 0, self.top_dies[-1]), (Qt.ItemDataRole.ForegroundRole, Qt.ItemDataRole.FontRole))

    def has_highlight(self, key):
        return bool(self.highlight_condition and key in self.highlight_condition)
    
    def has_any_highlights(self):
        return bool(self.highlight_condition and len(self.highlight_condition))

    def set_prefix(self, prefix):
        if prefix != self.prefix:
            self.prefix = prefix
            self.dataChanged.emit(
                self.createIndex(0, 0, self.top_dies[0]),
                self.createIndex(len(self.top_dies)-1, 0, self.top_dies[-1]))    

    # returns the model index of the selection, or None
    def set_sortcus(self, sortcus, sel):
        if sortcus != self.sortcus:
            sel_die = sel.internalPointer() if sel.isValid() else None
            self.beginResetModel()
            self.sortcus = sortcus
            #Resort the CUs, reload the top_dies
            di = self.top_dies[0].dwarfinfo
            sort_key = cu_sort_key if self.sortcus else lambda cu: cu.cu_offset
            di._CUs.sort(key = sort_key)
            for (i, cu) in enumerate(di._CUs):
                cu._i = i
                self.top_dies[i] = cu.get_top_DIE() # Already decorated, but the index is off
                self.top_dies[i]._i = i
            # Reload
            self.endResetModel()
            if sel_die:
                if sel_die.get_parent(): # Not a top level
                    return sel
                else:
                    return self.createIndex(0, sel_die._i, sel_die)

    # Returns the index of the new selection, if any
    def set_sortdies(self, sortdies):
        if sortdies != self.sortdies:
            self.sortdies = sortdies
            self.beginResetModel()
            for (i, die) in enumerate(self.top_dies):
                # Fragile! We invalidate the children in the decorated DIEs in the CU DIE cache
                # To force reloading and sorting
                for top_die in self.top_dies:
                    for die in top_die.cu._dielist:
                        die._children = None
            self.endResetModel()
            return self.createIndex(0, 0, self.top_dies[0])

    # Identifier for the current tree node that you can navigate to
    # For the back-forward logic
    # Specifically, (cu, offset within the info section)
    def get_navitem(self, index):
        die = index.internalPointer()
        return (die.cu, die.offset) if die else None # Issue # 1473, weird.

    # navitem is (CU, offset within the info section)
    # returns an index within the tree
    def index_for_navitem(self, navitem):
        target_cu, target_offset = navitem
        # Random access is a tricky proposition in the current version. Parse the whole CU.
        for _ in target_cu.iter_DIEs():
            pass

        # Abusing the structure of the per-CU DIE cache of pyelftools, it's the same in DWWARFv1
        i = bisect_left(target_cu._diemap, target_offset)
        if i >= len(target_cu._diemap) or target_cu._diemap[i] != target_offset:
            return None
        target_die = target_cu._dielist[i]
        if target_die.is_null():
            return None
        return self.index_for_die(target_die)

    # Takes a die that might not have an _i
    # Restores the _i
    # Assumes some parent DIEs of the current one are already parsed
    # and cached in the CU, so get_parent will always return a valid parent DIE
    def index_for_die(self, die):
        if hasattr(die, '_i'): # DIE already iterated over
            return self.createIndex(die._i, 0, die)
        else: # Found the DIE, but the tree was never opened this deep. Read the tree along the path to the target DIE
            index = False
            while not hasattr(die, '_i'):
                parent_die = die.get_parent()
                load_children(parent_die, self.sortdies) # This will populate the _i in all children of parent_die, including die
                if not index: # After the first iteration, the one in the direct parent of target_die, target_die will have _i
                    if die.is_null():
                        die = parent_die._children[-1] # Null is a terminator in a sequence - move to the sibling
                        # TODO: move to the closest in terms of offset, which would require going down the nearest sibling's tree
                    index = self.createIndex(die._i, 0, die)
                die = parent_die
            return index

    # Returns the index of the found item, or False
    # start_pos is the index of the current item, or an invalid one
    # cond is a condition function
    # cu_cond is the same for CUs - hook for find by IP
    def find(self, start_pos, cond, cu_cond = False):
        have_start_pos = start_pos.isValid()
        if have_start_pos: # Searching from a specific position, with wrap-around
            start_die = start_pos.internalPointer()
            start_die_offset = start_die.offset # In the current die, before the next one
            start_cu = start_die.cu
            start_cu_offset = start_cu.cu_offset
            cu = start_cu
            wrapped = False
        else:
            cu = self.top_dies[0].cu

        while True:
            cu_offset = cu.cu_offset
            # Parse all DIEs in the current CU
            if cu_cond(cu) if cu_cond else True:
                try: #1516
                    for die in cu.iter_DIEs():
                        # Quit condition with search from position - quit once we go past the starting position after the wrap
                        if have_start_pos and cu_offset >= start_cu_offset and die.offset > start_die_offset and wrapped:
                            break
                        if not die.is_null() and (not have_start_pos or cu_offset != start_cu_offset or (not wrapped and die.offset > start_die_offset)) and cond(die):
                            return self.index_for_die(die)
                except KeyError as exc: #1516
                    from .__main__ import version
                    from .crash import report_crash
                    from inspect import currentframe
                    tb = exc.__traceback__
                    ctxt = dict()
                    try:
                        ctxt['cu_offset'] = cu.cu_offset
                        ctxt['dwarf_config'] = cu.dwarfinfo.config
                        abbrev_codes = set(d.abbrev_code for d in cu._dielist if not d.is_null())
                        at = cu.get_abbrev_table()
                        format_attr_in_abbrev = lambda a: (a.name, a.form, a.value) if a.value is not None else (a.name, a.form)
                        format_abbr = lambda ab: (ab.decl.tag, ab._has_children, tuple(format_attr_in_abbrev(a) for a in ab.decl.attr_spec))
                        ctxt['abbrevs'] = {c: format_abbr(at.get_abbrev(c)) for c in abbrev_codes}
                        stm = cu.dwarfinfo.debug_info_sec.stream
                        crash_pos = ctxt['crash_pos'] = stm.tell()
                        slice = stm.getbuffer()[cu.cu_offset:crash_pos+1]
                        ctxt['cu_in_info'] =  ' '.join("%02x" % b for b in slice)
                    except Exception:
                        pass
                    report_crash(exc, tb, version, currentframe(), ctxt)

                    QApplication.instance().win.show_warning("This executable file is corrupt or incompatible with the current version of DWARF Explorer. Please consider creating a new issue at https://github.com/sevaa/dwex/issues, and share this file with the tech support.")
                    return False

            # We're at the end of the CU. What next?
            if cu._i < len(self.top_dies) - 1: # More CUs to scan
                cu = self.top_dies[cu._i + 1].cu
            elif have_start_pos and not wrapped: # Scanned the last CU, wrap around
                cu = self.top_dies[0].cu
                wrapped = True
            else:
                break

        return False

    # Search back - same idea
    def find_back(self, start_pos, cond, cu_cond = False):
        have_start_pos = start_pos.isValid()
        if have_start_pos: # Searching from a specific position, with wrap-around
            start_die = start_pos.internalPointer()
            start_die_offset = start_die.offset # In the current die, before the next one
            start_cu = start_die.cu
            start_cu_offset = start_cu.cu_offset
            cu = start_cu
            wrapped = False
        else:
            cu = self.top_dies[-1].cu

        while True:
            cu_offset = cu.cu_offset
            # Parse all DIEs in the current CU
            if cu_cond(cu) if cu_cond else True:
                for die in cu.iter_DIEs(): # Fill the DIE cache
                    pass

                # Abusing the internal cache of pyelftools - fragile!

                if have_start_pos and not wrapped and cu_offset == start_cu_offset:
                    i = bisect_left(cu._diemap, start_die_offset-1)-1
                else:
                    i = len(cu._diemap) - 1

                while i >= 0:
                    die = cu._dielist[i]
                    if not die.is_null():
                        # Quit condition with search from position - quit once we go past the starting position after the wrap
                        if have_start_pos and die.offset == start_die_offset and wrapped:
                            return False
                        if cond(die):
                            return self.index_for_die(die)
                    i -= 1

            # We're at the end of the CU. What next?
            if cu._i > 0: # More CUs to scan
                cu = self.top_dies[cu._i - 1].cu
            elif have_start_pos and not wrapped: # Scanned the last CU, wrap around
                cu = self.top_dies[-1].cu
                wrapped = True
            else:
                break

        return False            

    
    def find_offset(self, offset):
        cu = next((td.cu
            for td
            in self.top_dies
            if 0 <= offset-td.cu.cu_die_offset < td.cu.header.unit_length), False)
        if not cu:
            return None
        # On an off chance it's already parsed and the offset is precise
        i = bisect_right(cu._diemap, offset)
        if offset == cu._diemap[i - 1]:
            return self.index_for_die(cu._dielist[i - 1])
        # Now the hard way
        # It would be possible to optimize that, parse not all DIEs but just some
        # But let's not.
        for die in cu.iter_DIEs():
            pass
        i = bisect_right(cu._diemap, offset)
        return self.index_for_die(cu._dielist[i - 1])

