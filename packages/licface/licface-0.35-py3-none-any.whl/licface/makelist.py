#!/usr/bin/env python3
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-08-27 09:03:38.459075
# Description: Make a list see like table (custom rows/custom cols)
# License: MIT

HAS_RICH = False
HAS_PRETTY_TABLE = False
HAS_MAKE_COLORS = False

try:
    from rich.table import Table
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from packaging.version import Version
    import prettytable as ptt
    assert Version(ptt.__version__) >= Version('0.7')
    HAS_PRETTY_TABLE = True
except (ImportError, AssertionError):
    HAS_PRETTY_TABLE = False

try:
    import make_colors
    HAS_MAKE_COLORS = True
except ImportError:
    HAS_MAKE_COLORS = False


class MakeList:
    """
    MakeList
    ========
    Class-level utility for creating a table-like textual display from a flat list of items.
    Supports three rendering backends (chosen automatically if available): Rich, PrettyTable,
    or a simple built-in text fallback. Provides flexible layout and color control.
    Key features
    ------------
    - Arrange items into a grid with a specified number of columns.
    - Option to fill the grid vertically (column-major) or horizontally (row-major).
    - Optional integration with the Rich library for styled console tables.
    - Optional integration with PrettyTable for nicely formatted ASCII tables.
    - Fallback simple formatter that produces a plain-text aligned table.
    - Per-column color specification via COLOR_RANGE, and default foreground/background
        control via FCOLOR/FORECOLOR/FOREGROUNDCOLOR/FRCOLOR and BCOLOR/BACKCOLOR/BACKGROUNDCOLOR/BGCOLOR.
    - Methods provided: makeList (primary), make (alias), set (alias), and test (example runner).
    Public class attributes (defaults)
    ----------------------------------
    - FCOLOR, FORECOLOR, FOREGROUNDCOLOR, FRCOLOR: default foreground color string.
        Default value is "#00FFFF" (treated as the sentinel default color).
    - BCOLOR, BACKCOLOR, BACKGROUNDCOLOR, BGCOLOR: default background color string or None.
    - COLOR_RANGE: list where each element may be a color name (str) or a (fg, bg) pair
        to specify per-column styling for the Rich table backend.
    Main method: makeList(data_list, ncols, vertically=True, show=False, justify="left",
                                                no_wrap=True, use_rich=False, use_prettytable=False)
    ---------------------------------------------------------------------------
    Parameters:
    - data_list (Sequence): Flat list of items to display. If empty or falsy, returns "".
    - ncols (int): Number of columns in the output grid.
    - vertically (bool): If True (default), fill columns top-to-bottom then left-to-right
        (column-major). If False, fill rows left-to-right then top-to-bottom (row-major).
    - show (bool): If True the method prints the table and returns None. If False it
        returns the generated string representation.
    - justify (str): Horizontal justification applied to columns (Rich backend). One of
        "left" (default), "right", or "center".
    - no_wrap (bool): Pass-through to Rich column configuration; if True the text is not wrapped.
    - use_rich (bool): When True, attempt to render using Rich (if available).
    - use_prettytable (bool): When True, attempt to render using PrettyTable (if available).
    Return value:
    - When show is True: prints to stdout / console and returns None.
    - When show is False: returns the table as a string (Rich/PrettyTable output or plain text).
    Behavior details
    ----------------
    - The method computes the number of rows by ceiling division: rows = ceil(len(data_list) / ncols).
    - Data is partitioned into chunks of length equal to the row count (for vertical filling) or
        into row-length segments (for horizontal filling). Missing cells in the last chunk are padded
        with empty strings so the grid is regularly shaped.
    - If Rich is selected and available, columns are added to a Rich Table with per-column style
        determined by COLOR_RANGE or the default foreground/background attributes.
    - If PrettyTable is selected and available, a header-less PrettyTable is created and optionally
        colored via an external make_colors helper if that helper is present.
    - If neither Rich nor PrettyTable is available, a plain-text aligned table is produced using
        column width computation and left-justification. Columns are separated by two spaces.
    Color handling
    --------------
    - COLOR_RANGE: if non-empty and contains entries for column indices, each entry may be:
        - a single color string (foreground) or
        - a 2-tuple/list (foreground, background).
        When present, COLOR_RANGE takes precedence for column styles in the Rich backend.
    - Default foreground color is resolved by checking FCOLOR, FORECOLOR, FOREGROUNDCOLOR, FRCOLOR
        in that order and picking the first value not equal to the sentinel "#00FFFF".
    - Default background color is resolved by checking BCOLOR, BACKCOLOR, BACKGROUNDCOLOR, BGCOLOR
        in that order and picking the first non-None value.
    - When a background is set, column style strings are returned as "fg on bg" for Rich.
    Aliases
    -------
    - make(...) and set(...) are thin aliases for makeList(...).
    Testing helper
    --------------
    - test() demonstrates typical usage patterns with sample data and will exercise Rich and
        PrettyTable rendering if those libraries are available in the runtime.
    Usage examples
    --------------
    Simple usage (return string):
    >>> doc = MakeList.makeList(['apple','banana','cherry','date'], ncols=2, show=False)
    >>> print(type(doc))
    <class 'str'>
    >>> print(doc)
    apple   banana
    cherry  date
    Print directly (no return):
    >>> MakeList.makeList(['a','b','c','d','e'], ncols=3, show=True)
    Vertical vs horizontal fill:
    >>> # Vertical (column-major)
    >>> MakeList.makeList(['1','2','3','4','5','6'], ncols=3, vertically=True, show=True)
    >>> # Horizontal (row-major)
    >>> MakeList.makeList(['1','2','3','4','5','6'], ncols=3, vertically=False, show=True)
    Using Rich (if installed):
    >>> MakeList.makeList(['x','y','z','w'], ncols=2, use_rich=True, show=True)
    Using PrettyTable (if installed):
    >>> MakeList.makeList(['x','y','z','w'], ncols=2, use_prettytable=True, show=True)
    Per-column color example for Rich (conceptual):
    >>> MakeList.COLOR_RANGE = [['red','black'], ['green'], 'yellow']
    >>> MakeList.FCOLOR = '#00FFFF'   # sentinel default — overridden by COLOR_RANGE entry
    Notes
    -----
    - This class does not mutate the input list.
    - Column count (ncols) must be >= 1.
    - If optional third-party libraries are available, they will be used unless explicitly
        bypassed by the force flags (use_rich/use_prettytable).
    
    """
    
    FCOLOR = FORECOLOR = FOREGROUNDCOLOR = FRCOLOR = "#00FFFF"
    BCOLOR = BACKCOLOR = BACKGROUNDCOLOR = BGCOLOR = None
    COLOR_RANGE = []

    @classmethod
    def makeList(cls, data_list, ncols, vertically=True, show=False, justify="left", 
                 no_wrap=True, use_rich=False, use_prettytable=False):
        """
        Create a table-like display from a list of data.
        
        Args:
            data_list: List of items to display
            ncols: Number of columns
            vertically: Fill table vertically (True) or horizontally (False)
            show: Whether to print the table
            justify: Text justification ('left', 'right', 'center')
            no_wrap: Whether to wrap text
            use_rich: Force use of rich library
            use_prettytable: Force use of prettytable library
            
        Returns:
            String representation of the table or None if printed directly
        """
        if not data_list:
            return ""

        # Calculate rows and columns
        L = data_list
        nrows = -((-len(L)) // ncols)  # Ceiling division
        
        # Determine which library to use
        if use_rich and HAS_RICH:
            return cls._create_rich_table(L, nrows, ncols, vertically, show, justify, no_wrap)
        elif (use_prettytable and HAS_PRETTY_TABLE) or HAS_PRETTY_TABLE:
            return cls._create_pretty_table(L, nrows, ncols, vertically, show)
        else:
            # Fallback to simple text table
            return cls._create_simple_table(L, nrows, ncols, vertically, show)

    @classmethod
    def _create_rich_table(cls, L, nrows, ncols, vertically, show, justify, no_wrap):
        """Create a Rich table from a list of data.

        Args:
            cls(type): The class this method is bound to.
            L(list): List of data to populate the table.
            nrows(int): Number of rows in the table.
            ncols(int): Number of columns in the table.
            vertically(bool): Whether to arrange data vertically or horizontally.
            show(bool): Whether to print the table to the console.
            justify(str): Justification of text within cells.
            no_wrap(bool): Whether to disable text wrapping.

        Returns:
            Union[str, None]: String representation of the table if show is False, otherwise None.

        Raises:
            Exception: Generic exception during table creation or rendering.
        """
        
        r = nrows if vertically else ncols
        
        # Split data into chunks
        chunks = [L[i:i + r] for i in range(0, len(L), r)]
        if chunks:  # Ensure chunks is not empty
            chunks[-1].extend(['' for _ in range(r - len(chunks[-1]))])
        
        if vertically and chunks:
            chunks = list(zip(*chunks))

        # Create Rich table
        table = Table(show_header=False, show_lines=False, box=None, pad_edge=False) # type: ignore
        
        # Add columns with proper color handling
        for i in range(ncols):
            style = cls._get_column_style(i)
            table.add_column(justify=justify, no_wrap=no_wrap, style=style)

        # Add rows
        for row in chunks:
            table.add_row(*[str(item) for item in row])
        
        if show:
            console.print(table)
            return None
        else:
            # Return string representation
            with console.capture() as capture:
                console.print(table)
            return capture.get()

    @classmethod
    def _create_pretty_table(cls, L, nrows, ncols, vertically, show):
        """Creates and displays or returns a pretty table from a list.

        Args:
            cls(object): Class object.
            L(list): List of items to display in the table.
            nrows(int): Number of rows in the table.
            ncols(int): Number of columns in the table.
            vertically(bool): If True, arranges items vertically; otherwise, horizontally.
            show(bool): If True, prints the table and returns None; otherwise, returns the table string.

        Returns:
            str or None: If show is True, returns None; otherwise, returns the formatted table string.

        Raises:
            ValueError: If input list L is empty or dimensions are invalid.
        """
        
        t = ptt.PrettyTable([str(x) for x in range(ncols)]) # type: ignore
        t.header = False
        t.align = 'l'
        t.hrules = ptt.NONE # type: ignore
        t.vrules = ptt.NONE # type: ignore
        
        r = nrows if vertically else ncols
        chunks = [L[i:i + r] for i in range(0, len(L), r)]
        if chunks:
            chunks[-1].extend(['' for _ in range(r - len(chunks[-1]))])
        
        if vertically and chunks:
            chunks = list(zip(*chunks))
        
        for chunk in chunks:
            t.add_row([str(item) for item in chunk])
        
        table_str = str(t)
        
        # Apply colors if available
        if HAS_MAKE_COLORS:
            fg_color = cls._get_foreground_color()
            bg_color = cls._get_background_color()
            color_args = [fg_color] + ([bg_color] if bg_color else [])
            table_str = make_colors.make_colors(table_str, *color_args) # type: ignore
        
        if show:
            print(table_str)
            return None
        return table_str

    @classmethod
    def _create_simple_table(cls, L, nrows, ncols, vertically, show):
        """Creates a simple table from a list.

        Args:
            cls(type): The class this method is bound to.
            L(list): The list of items to display in the table.
            nrows(int): Number of rows in the table.
            ncols(int): Number of columns in the table.
            vertically(bool): If True, arranges items vertically; otherwise, horizontally.
            show(bool): If True, prints the table and returns None; otherwise, returns the table as a string.

        Returns:
            str or None: The formatted table as a string if show is False, otherwise None.

        Raises:
            ValueError: If input data is invalid or dimensions are inconsistent.
        """
        
        r = nrows if vertically else ncols
        chunks = [L[i:i + r] for i in range(0, len(L), r)]
        if chunks:
            chunks[-1].extend(['' for _ in range(r - len(chunks[-1]))])
        
        if vertically and chunks:
            chunks = list(zip(*chunks))
        
        # Calculate column widths
        if chunks:
            col_widths = [max(len(str(row[i])) if i < len(row) else 0 
                            for row in chunks) for i in range(ncols)]
        else:
            col_widths = [0] * ncols
        
        # Create formatted rows
        formatted_rows = []
        for row in chunks:
            formatted_row = []
            for i, item in enumerate(row):
                if i < len(col_widths):
                    formatted_row.append(str(item).ljust(col_widths[i]))
                else:
                    formatted_row.append(str(item))
            formatted_rows.append('  '.join(formatted_row))
        
        result = '\n'.join(formatted_rows)
        
        if show:
            print(result)
            return None
        return result

    @classmethod
    def _get_column_style(cls, column_index):
        """Get style for a specific column in Rich table.

        Args:
            cls(type): Class object.
            column_index(int): Index of the column.

        Returns:
            str: Style string for the column, or None if no style is defined.

        Raises:
            IndexError: If column_index is out of bounds for cls.COLOR_RANGE.
            TypeError: If cls.COLOR_RANGE contains invalid data types.
        """
        
        if cls.COLOR_RANGE and column_index < len(cls.COLOR_RANGE):
            color_def = cls.COLOR_RANGE[column_index]
            if isinstance(color_def, (list, tuple)):
                if len(color_def) >= 2:
                    return f'{color_def[0]} on {color_def[1]}'
                elif len(color_def) == 1:
                    return str(color_def[0])
        
        # Default color handling
        fg_color = cls._get_foreground_color()
        bg_color = cls._get_background_color()
        
        if bg_color:
            return f'{fg_color} on {bg_color}'
        return fg_color

    @classmethod
    def _get_foreground_color(cls):
        """Get the foreground color."""
        colors = [cls.FCOLOR, cls.FORECOLOR, cls.FOREGROUNDCOLOR, cls.FRCOLOR]
        return next((color for color in colors if color != "#00FFFF"), "#00FFFF")

    @classmethod
    def _get_background_color(cls):
        """Get the background color."""
        colors = [cls.BCOLOR, cls.BACKCOLOR, cls.BACKGROUNDCOLOR, cls.BGCOLOR]
        return next((color for color in colors if color is not None), None)

    @classmethod
    def make(cls, *args, **kwargs):
        """Factory method to create an instance of the class.

        Args:
            cls(type): Class to instantiate.
            args(tuple): Positional arguments passed to the makeList method.
            kwargs(dict): Keyword arguments passed to the makeList method.

        Returns:
            object: An instance of the class cls.

        Raises:
            Exception: Any exception raised by the makeList method.
        """
        return cls.makeList(*args, **kwargs)
    
    @classmethod
    def set(cls, *args, **kwargs):
        """Set function.

        Args:
            args(Any): Variable length argument list.
            kwargs(Any): Arbitrary keyword arguments.

        Returns:
            list: A list created from the input arguments.

        Raises:
            Exception: Generic exception during list creation.
        """
        return cls.makeList(*args, **kwargs)

    @classmethod
    def test(cls):
        # Example usage and testing
        # Test data
        test_data = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape', 'honeydew']
        
        print("=== Simple Table Test === (ncols = 3)")
        result = MakeList.makeList(test_data, ncols=3, show=True)
        
        print("\n=== Horizontal Fill === (ncols = 3)")
        MakeList.makeList(test_data, ncols=3, vertically=False, show=True)
        
        print("\n=== Return String (not print) === (ncols = 2)")
        table_str = MakeList.makeList(test_data, ncols=2, show=False)
        print("Returned string:")
        print(repr(table_str))

        print("=== Simple Table Test === (ncols = 2)")
        result = MakeList.makeList(test_data, ncols=2, show=True)
        
        print("\n=== Horizontal Fill === (ncols = 2)")
        MakeList.makeList(test_data, ncols=3, vertically=False, show=True)
        
        print("\n=== Return String (not print) === (ncols = 3)")
        table_str = MakeList.makeList(test_data, ncols=3, show=False)
        print("Returned string:")
        print(repr(table_str))
        
        
        # Test with Rich if available
        if HAS_RICH:
            print("\n=== Rich Table Test === (ncols = 3)")
            MakeList.makeList(test_data, ncols=3, use_rich=True, show=True)

            print("\n=== Rich Table Test === (ncols = 2)")
            MakeList.makeList(test_data, ncols=2, use_rich=True, show=True)
        
        # Test with PrettyTable if available
        if HAS_PRETTY_TABLE:
            print("\n=== PrettyTable Test === (ncols = 3)")
            MakeList.makeList(test_data, ncols=3, use_prettytable=True, show=True)

            print("\n=== PrettyTable Test === (ncols = 2)")
            MakeList.makeList(test_data, ncols=2, use_prettytable=True, show=True)

        print("\n- FOREGROUND VARIABLES:")
        print(f"\t 'FCOLOR' or 'FORECOLOR' or 'FOREGROUNDCOLOR' or 'FRCOLOR', default value #00FFFF")

        print("- BACKGROUND VARIABLES:")
        print(f"\t 'BCOLOR' or 'BACKCOLOR' or 'BACKGROUNDCOLOR' or 'BGCOLOR', default value None")

        print("* or use 'COLOR_RANGE' which must list in list format")
        
    @classmethod
    def main(cls):
        return cls.test()

if __name__ == "__main__":
    MakeList.test()