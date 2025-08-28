from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from .shape import Shape
from .helper import Helper


@dataclass
class Grid:
    _pools: list = field(init=False, default_factory=list)
    _grid: dict = field(init=False, default_factory=dict)

    def set_grid(self, pools: list):
        """Set the grid for the process map"""

        self._pools = pools
        self._grid = {}
        # self.set_shapes_position(None, self._find_start_shape(), 0)

        # Process all disconnected segments and unconnected shapes
        self._process_all_shapes()

    def get_grid_items(self):
        """Get the grid items"""

        return self._grid.items()

    def is_same_lane(self, previous_shape: Shape, current_shape: Shape) -> bool:
        """Check if the previous shape and current shape are in the same lane"""

        return previous_shape.lane_id == current_shape.lane_id

    def is_same_pool(self, previous_shape: Shape, current_shape: Shape) -> bool:
        """Check if the previous shape and current shape are in the same pool"""
        return previous_shape.pool_name == current_shape.pool_name

    def set_shapes_position(
        self,
        previous_shape: Shape,
        current_shape: Shape,
        index: int = 0,
    ):
        """Set the position of the shapes in the grid"""
        if current_shape.grid_traversed is True:
            Helper.printc(
                f"[orange4]{current_shape.name} is already traversed[/]",
                show_level="layout_grid",
            )
            return
        Helper.printc(
            f"Traversing [red]{current_shape.name}[/]", show_level="layout_grid"
        )
        current_shape.grid_traversed = True
        self.add_shape_to_grid(previous_shape, current_shape, index)
        for connection_index, next_connection in enumerate(current_shape.connection_to):
            next_shape = next_connection.target
            Helper.printc(
                f"    [dodger_blue1]{connection_index}: {current_shape.name} -> {next_shape.name}[/]",
                show_level="layout_grid",
            )
            self.set_shapes_position(current_shape, next_shape, connection_index)
        Helper.printc(
            f"Done traversing [:thumbsup: {current_shape.name}]",
            show_level="layout_grid",
        )

    def add_shape_to_grid(
        self, previous_shape: Shape, current_shape: Shape, index: int
    ):
        """Add the shape to the grid"""
        # ---If previous_shape is None, it is the start shape---
        if previous_shape is None:
            # ---Add the start shape to the grid---
            Helper.printc(
                f"    ==>Start adding [{current_shape.name}] to grid (append)",
                show_level="layout_grid",
            )
            self.add_shape_to_lane_row(current_shape.lane_id, 1, current_shape)
        else:
            (
                _,
                previous_shape_row_number,
                previous_shape_col_number,
            ) = self.get_shape_lane_rowcolumn(previous_shape)

            if self.is_same_lane(previous_shape, current_shape):
                # Same lane

                if index == 0:
                    Helper.printc(
                        (
                            "        ==>Same lane (row 0): ",
                            f"add_shape_to_lane [{current_shape.name}],",
                            f" {previous_shape_row_number=}",
                        ),
                        show_level="layout_grid",
                    )
                    self.add_shape_to_lane(
                        current_shape.lane_id, previous_shape_row_number, current_shape
                    )
                else:  ### Next row
                    Helper.printc(
                        f"        ==>Same lane (next row): add_shape_to_lane_rowcolumn [{current_shape.name}, {previous_shape_col_number}]",
                        show_level="layout_grid",
                    )
                    if self.is_column_empty(
                        current_shape.lane_id,
                        previous_shape_row_number,
                        previous_shape_col_number,
                    ):
                        Helper.printc("Is empty", 34, show_level="layout_grid")
                        self.add_shape_to_lane_rowcolumn(
                            current_shape.lane_id,
                            previous_shape_row_number,
                            previous_shape_col_number,
                            current_shape,
                        )
                    else:
                        Helper.printc("Not empty", 34, show_level="layout_grid")
                        Helper.printc(
                            f"Adding shape to {index + 1}, {previous_shape_col_number}",
                            show_level="layout_grid",
                        )
                        self.add_shape_to_lane_rowcolumn(
                            current_shape.lane_id,
                            index + 1,
                            previous_shape_col_number + 1,
                            # previous_shape_col_number,
                            current_shape,
                        )
            elif index == 0:
                if self.is_same_pool(previous_shape, current_shape):
                    Helper.printc(
                        f"        ==> {index=}, Same pool, diff lane: add_shape_to_lane [{current_shape.name}], {previous_shape_row_number+1}",
                        show_level="layout_grid",
                    )
                    self.add_shape_to_lane_rowcolumn(
                        current_shape.lane_id,
                        index + 1,
                        previous_shape_col_number + 1,
                        current_shape,
                    )
                else:
                    # Different pool
                    Helper.printc(
                        f"        ==> {index=}, Diff pool: add_shape_to_lane_rowcolumn [{current_shape.name}, {previous_shape_col_number=}]",
                        show_level="layout_grid",
                    )
                    self.add_shape_to_lane_rowcolumn(
                        current_shape.lane_id,
                        index + 1,
                        previous_shape_col_number,
                        current_shape,
                    )
            else:
                if self.is_same_pool(previous_shape, current_shape):
                    Helper.printc(
                        f"        ==> {index=}, Same pool, diff lane: add_shape_to_lane_rowcolumn [{current_shape.name}], {previous_shape_col_number=}",
                        show_level="layout_grid",
                    )
                else:
                    # Different pool
                    Helper.printc(
                        f"        ==> {index=}, Diff pool: add_shape_to_lane_rowcolumn [{current_shape.name}, {previous_shape_col_number=}]",
                        show_level="layout_grid",
                    )

                self.add_shape_to_lane_rowcolumn(
                    current_shape.lane_id,
                    index,
                    previous_shape_col_number,
                    current_shape,
                )

    def _find_start_shape(self) -> Shape:
        """Find the start shape in the process map"""
        for pool in self._pools:
            for lane in pool.lanes:
                for shape in lane.shapes:
                    ### If the shape has no connection_from, it is the start shape
                    Helper.printc(
                        f"{shape.name} - {len(shape.connection_from)}",
                        show_level="layout_grid",
                    )
                    if len(shape.connection_from) == 0:
                        return shape
        return None

    def get_all_shapes(self) -> list:
        """Get all the shapes points"""
        shapes = []
        for _, lane in self._grid.items():
            for _, col in lane.items():
                for item in col:
                    if item is not None:
                        shapes.append(item)
        return shapes

    def _process_all_shapes(self):
        """Process all shapes including disconnected segments and unconnected shapes"""

        # Step 1: Find all shapes with no incoming connections
        no_incoming_shapes = self._find_all_start_shapes()
        
        # Get the first lane IDs from all pools
        first_lane_ids = self._get_first_lane_ids_from_pools()
        
        # Identify mid-flow terminators, true start shapes, and disconnected shapes
        true_start_shapes = []
        disconnected_shapes = []
        mid_flow_terminators = []
        
        for shape in no_incoming_shapes:
            # Check if this is a terminator with outgoing connections (mid-flow terminator)
            if len(shape.connection_to) > 0 and hasattr(shape, '__class__') and shape.__class__.__name__ == 'Terminator':
                # This is a mid-flow terminator that needs special positioning
                mid_flow_terminators.append(shape)
            elif len(shape.connection_to) > 0:
                # This is a true start shape (has outgoing connections but is not a terminator)
                true_start_shapes.append(shape)
            else:
                # This is a completely disconnected shape
                disconnected_shapes.append(shape)
        
        # First, process regular shapes to ensure the main flow is established
        # Group true start shapes by lane for parallel layout
        start_shapes_by_lane = {}
        for start_shape in true_start_shapes:
            if start_shape.lane_id not in start_shapes_by_lane:
                start_shapes_by_lane[start_shape.lane_id] = []
            start_shapes_by_lane[start_shape.lane_id].append(start_shape)
        
        # Process each lane's true start shapes
        for lane_id, lane_start_shapes in start_shapes_by_lane.items():
            # If multiple start nodes in the FIRST lane, arrange them vertically
            # For all other lanes, use standard horizontal layout
            if len(lane_start_shapes) > 1 and lane_id in first_lane_ids:
                for idx, start_shape in enumerate(lane_start_shapes):
                    if not start_shape.grid_traversed:
                        Helper.printc(
                            f"Processing start shape [{start_shape.name}] in vertical arrangement (position {idx+1})",
                            show_level="layout_grid",
                        )
                        # Use row number based on index to create vertical arrangement
                        self._add_start_node_to_grid(start_shape, idx+1)
            else:
                # Process normally (horizontal layout)
                for start_shape in lane_start_shapes:
                    if not start_shape.grid_traversed:
                        Helper.printc(
                            f"Processing start shape [{start_shape.name}]",
                            show_level="layout_grid",
                        )
                        self.set_shapes_position(None, start_shape, 0)
        
        # AFTER processing regular nodes, now position the mid-flow terminators
        # This ensures they don't interfere with the regular flow layout
        self._process_mid_flow_terminators(mid_flow_terminators)
        
        # Process completely disconnected shapes - arrange horizontally in each lane
        disconnected_by_lane = {}
        for shape in disconnected_shapes:
            if shape.lane_id not in disconnected_by_lane:
                disconnected_by_lane[shape.lane_id] = []
            disconnected_by_lane[shape.lane_id].append(shape)
            
        for lane_id, lane_shapes in disconnected_by_lane.items():
            Helper.printc(
                f"Processing {len(lane_shapes)} disconnected shapes in lane {lane_id}",
                show_level="layout_grid",
            )
            for col_idx, shape in enumerate(lane_shapes, 1):
                if not shape.grid_traversed:
                    Helper.printc(
                        f"Adding disconnected shape [{shape.name}] horizontally at col {col_idx}",
                        show_level="layout_grid",
                    )
                    shape.grid_traversed = True
                    # Force all disconnected shapes to be in row 1 with different columns for horizontal layout
                    self.add_shape_to_lane_rowcolumn(lane_id, 1, col_idx, shape)

        # Step 3: Handle any remaining unprocessed shapes
        self._add_remaining_unconnected_shapes()
        
    def _process_mid_flow_terminators(self, mid_flow_terminators):
        """Process mid-flow terminators with special positioning logic"""
        for terminator in mid_flow_terminators:
            if terminator.grid_traversed:
                continue
                
            # A mid-flow terminator should have exactly one outgoing connection
            if len(terminator.connection_to) != 1:
                Helper.printc(
                    f"Warning: Mid-flow terminator [{terminator.name}] has {len(terminator.connection_to)} outgoing connections",
                    show_level="layout_grid",
                )
                # Process as a normal start shape if it doesn't fit our expectations
                self.set_shapes_position(None, terminator, 0)
                continue
                
            # Get the target node
            target_shape = terminator.connection_to[0].target
            target_lane_id = target_shape.lane_id
            
            # Skip if target node is not positioned yet (which should not happen since we processed all regular nodes first)
            if not target_shape.grid_traversed:
                Helper.printc(
                    f"Target shape [{target_shape.name}] not positioned yet, using default positioning",
                    show_level="layout_grid",
                )
                self.set_shapes_position(None, terminator, 0)
                continue
            
            # Now position the terminator based on target position
            Helper.printc(
                f"Positioning mid-flow terminator [{terminator.name}] relative to target [{target_shape.name}]",
                show_level="layout_grid",
            )
            
            # Check if terminator is in the same lane as its target
            if terminator.lane_id == target_lane_id:
                self._position_same_lane_terminator(terminator, target_shape)
            else:
                self._position_different_lane_terminator(terminator, target_shape)
                
    def _position_same_lane_terminator(self, terminator, target_shape):
        """Position a mid-flow terminator that is in the same lane as its target"""
        # Get target shape's lane, row, and column
        lane_id, target_row, target_col = self.get_shape_lane_rowcolumn(target_shape)
        
        if lane_id is None:
            # Target not properly positioned, fall back to normal processing
            Helper.printc(
                f"Target shape [{target_shape.name}] not found in grid, using default positioning",
                show_level="layout_grid",
            )
            self.set_shapes_position(None, terminator, 0)
            return
            
        Helper.printc(
            f"Same-lane terminator: target at lane {lane_id}, row {target_row}, col {target_col}",
            show_level="layout_grid",
        )
        
        # First try to place to the left of the target if possible
        if target_col > 1 and self.is_column_empty(lane_id, target_row, target_col - 1):
            Helper.printc(
                f"Placing terminator to the left of target at col {target_col - 1}",
                show_level="layout_grid",
            )
            self.add_shape_to_lane_rowcolumn(lane_id, target_row, target_col - 1, terminator)
            terminator.grid_traversed = True
            return
            
        # If left side is occupied, try to place to the right
        right_col = target_col + 1
        if self.is_column_empty(lane_id, target_row, right_col):
            Helper.printc(
                f"Placing terminator to the right of target at col {right_col}",
                show_level="layout_grid",
            )
            self.add_shape_to_lane_rowcolumn(lane_id, target_row, right_col, terminator)
            terminator.grid_traversed = True
            return
            
        # If neither side works, try below the target
        row_below = target_row + 1
        if not self._is_row_column_occupied(lane_id, row_below, target_col):
            Helper.printc(
                f"Placing terminator below target at row {row_below}, col {target_col}",
                show_level="layout_grid",
            )
            self.add_shape_to_lane_rowcolumn(lane_id, row_below, target_col, terminator)
            terminator.grid_traversed = True
            return
            
        # If below is occupied, try above
        row_above = target_row - 1
        if row_above > 0 and not self._is_row_column_occupied(lane_id, row_above, target_col):
            Helper.printc(
                f"Placing terminator above target at row {row_above}, col {target_col}",
                show_level="layout_grid",
            )
            self.add_shape_to_lane_rowcolumn(lane_id, row_above, target_col, terminator)
            terminator.grid_traversed = True
            return
            
        # If all preferred positions are taken, fall back to standard positioning
        Helper.printc(
            f"No ideal position available for terminator, using next available column",
            show_level="layout_grid",
        )
        next_col = self.get_next_column(lane_id, target_row)
        self.add_shape_to_lane_rowcolumn(lane_id, target_row, next_col, terminator)
        terminator.grid_traversed = True
        
    def _position_different_lane_terminator(self, terminator, target_shape):
        """Position a mid-flow terminator that is in a different lane from its target"""
        # Get target shape's position
        target_lane_id, target_row, target_col = self.get_shape_lane_rowcolumn(target_shape)
        terminator_lane_id = terminator.lane_id
        
        if target_lane_id is None:
            # Target not properly positioned, fall back to normal processing
            Helper.printc(
                f"Target shape [{target_shape.name}] not found in grid, using default positioning",
                show_level="layout_grid",
            )
            self.set_shapes_position(None, terminator, 0)
            return
            
        Helper.printc(
            f"Different-lane terminator: target at lane {target_lane_id}, row {target_row}, col {target_col}",
            show_level="layout_grid",
        )
        
        # When terminator is in a different lane, we want to:
        # 1. Align it vertically with its target (same column)
        # 2. If that's not possible, find the closest available column
        
        # First, try to place it in the same column as the target
        if not self._is_row_column_occupied(terminator_lane_id, 1, target_col):
            Helper.printc(
                f"Placing terminator vertically aligned with target at col {target_col}",
                show_level="layout_grid",
            )
            self.add_shape_to_lane_rowcolumn(terminator_lane_id, 1, target_col, terminator)
            terminator.grid_traversed = True
            return
            
        # Try columns close to the target column
        max_offset = 3  # Maximum number of columns to look on either side
        for offset in range(1, max_offset + 1):
            # Try column to the left
            left_col = target_col - offset
            if left_col > 0 and not self._is_row_column_occupied(terminator_lane_id, 1, left_col):
                Helper.printc(
                    f"Placing terminator at col {left_col}, offset {offset} left of target",
                    show_level="layout_grid",
                )
                self.add_shape_to_lane_rowcolumn(terminator_lane_id, 1, left_col, terminator)
                terminator.grid_traversed = True
                return
                
            # Try column to the right
            right_col = target_col + offset
            if not self._is_row_column_occupied(terminator_lane_id, 1, right_col):
                Helper.printc(
                    f"Placing terminator at col {right_col}, offset {offset} right of target",
                    show_level="layout_grid",
                )
                self.add_shape_to_lane_rowcolumn(terminator_lane_id, 1, right_col, terminator)
                terminator.grid_traversed = True
                return
                
        # If no position is available near the target column, use next available column
        Helper.printc(
            f"No column near target available, using next available column",
            show_level="layout_grid",
        )
        next_col = self.get_next_column(terminator_lane_id, 1)
        self.add_shape_to_lane_rowcolumn(terminator_lane_id, 1, next_col, terminator)
        terminator.grid_traversed = True
        
    def _is_row_column_occupied(self, lane_id, row_number, col_number):
        """Check if a specific row and column position is already occupied"""
        row_key = f"row{row_number}"
        
        # Check if lane exists in the grid
        if lane_id not in self._grid:
            return False
            
        # Check if row exists in the lane
        if row_key not in self._grid[lane_id]:
            return False
            
        # Check if column index is valid
        row_data = self._grid[lane_id][row_key]
        if col_number > len(row_data):
            return False
            
        # Check if position is occupied
        return row_data[col_number - 1] is not None
        
    def _add_start_node_to_grid(self, start_shape, row_number):
        """Add start node to grid in specified row and process its connections"""
        start_shape.grid_traversed = True
        # Add start node to specified row in column 1
        self.add_shape_to_lane_rowcolumn(start_shape.lane_id, row_number, 1, start_shape)
        
        # Process its connections similar to set_shapes_position
        for connection_index, next_connection in enumerate(start_shape.connection_to):
            next_shape = next_connection.target
            # Add the target node to the same row but next column
            if not next_shape.grid_traversed:
                next_shape.grid_traversed = True
                self.add_shape_to_lane_rowcolumn(next_shape.lane_id, row_number, 2, next_shape)
                # Continue processing subsequent connections
                for next_conn_idx, next_next_connection in enumerate(next_shape.connection_to):
                    next_next_shape = next_next_connection.target
                    self.set_shapes_position(next_shape, next_next_shape, next_conn_idx)

    def _find_all_start_shapes(self) -> list:
        """Find all shapes that could be start points (no incoming connections)"""
        start_shapes = []
        for pool in self._pools:
            for lane in pool.lanes:
                for shape in lane.shapes:
                    if len(shape.connection_from) == 0:
                        start_shapes.append(shape)
        return start_shapes

    def _add_remaining_unconnected_shapes(self):
        """Add any remaining unconnected shapes to the grid"""
        for pool in self._pools:
            for lane in pool.lanes:
                unconnected_shapes = [s for s in lane.shapes if not s.grid_traversed]

                if unconnected_shapes:
                    print(f"Processing {len(unconnected_shapes)} unconnected shapes in lane {lane.name}")
                    for shape in unconnected_shapes:
                        print(f"Shape: {shape.name}, connections from: {len(shape.connection_from)}, connections to: {len(shape.connection_to)}")
                    
                    # Use a fixed row for all completely disconnected shapes in each lane
                    # This ensures horizontal arrangement
                    for col_idx, shape in enumerate(unconnected_shapes, 1):
                        print(f"Adding unconnected shape [{shape.name}] at row 1, col {col_idx}")
                        shape.grid_traversed = True
                        # Force all shapes to be in row 1 with different columns for horizontal layout
                        self.add_shape_to_lane_rowcolumn(lane.id, 1, col_idx, shape)

    def _get_next_available_row(self, lane_id):
        """Get the next available row number for a lane"""
        if lane_id not in self._grid:
            return 1

        max_row = 0
        for row_key in self._grid[lane_id].keys():
            row_num = int(row_key.replace("row", ""))
            max_row = max(max_row, row_num)

        return max_row + 1
        
    def _get_first_lane_ids_from_pools(self):
        """Get the IDs of the first lane in each pool"""
        first_lane_ids = []
        for pool in self._pools:
            if pool.lanes:
                # Add the ID of the first lane in each pool
                first_lane_ids.append(pool.lanes[0].id)
        return first_lane_ids


    def add_shape_to_lane_row(self, lane_id: str, row_number: int, shape: Shape):
        """Add the shape to the lane row"""
        if lane_id not in self._grid:
            self._grid[lane_id] = {}
        row_number = f"row{row_number}"
        if row_number not in self._grid[lane_id]:
            self._grid[lane_id][row_number] = []
        Helper.printc(
            f"            ### ({shape.name=}), {lane_id=}, {row_number=}",
            36,
            show_level="layout_grid",
        )
        self._grid[lane_id][row_number].append(shape)

    def add_shape_to_lane_rowcolumn(
        self, lane_id: str, row_number: int, col_number: int, shape: Shape
    ):
        """Add the shape to the lane row column"""
        if lane_id not in self._grid:
            self._grid[lane_id] = {}

        row_number = f"row{row_number}"
        if row_number not in self._grid[lane_id]:
            self._grid[lane_id][row_number] = []

        # check if shape exists
        if self._grid[lane_id][row_number] is not None:
            if col_number > len(self._grid[lane_id][row_number]):
                for _ in range(col_number - len(self._grid[lane_id][row_number]) - 1):
                    self._grid[lane_id][row_number].append(None)
                self._grid[lane_id][row_number].append(shape)
            elif col_number == 1:
                self._grid[lane_id][row_number].append(shape)
            else:
                if self._grid[lane_id][row_number][col_number - 1] is None:
                    self._grid[lane_id][row_number][col_number - 1] = shape
                else:
                    self._grid[lane_id][row_number].append(shape)

        Helper.printc(
            f"            ### {shape.name=}, {lane_id=}, {row_number=}, {col_number=}",
            36,
            show_level="layout_grid",
        )

        ### add max columns to other lanes
        max_columns = self.get_max_column_count()
        for this_lane_id in self._grid:
            for row in self._grid[this_lane_id]:
                if len(self._grid[this_lane_id][row]) < max_columns:
                    for _ in range(max_columns - len(self._grid[this_lane_id][row])):
                        self._grid[this_lane_id][row].append(None)

    def find_shape_rowcolumn_in_lane(self, lane_id: str, shape: Shape):
        # sourcery skip: use-next
        """Find the shape row and column in the lane"""
        if lane_id not in self._grid:
            return None, None

        for row_number, col in self._grid[lane_id].items():
            if shape in col:
                return row_number, col.index(shape) + 1

        return None, None

    def get_column_index(self, lane_id: str, shape: Shape):
        """Get the column index of the shape in the lane"""
        # find shape column index
        for _, col in self._grid[lane_id].items():
            if shape in col:
                return col.index(shape) + 1

    def is_column_empty(self, lane_id: str, row_number: int, col_number: int):
        # sourcery skip: use-any
        """Check if the column is empty"""

        row_number = f"row{row_number}"
        for row, col in self._grid[lane_id].items():
            if row == row_number and col[col_number - 1] is not None:
                shape = col[col_number - 1]
                Helper.printc(f"            ### {shape.name}", show_level="layout_grid")
                return False
        return True

    def get_shape_lane_rowcolumn(self, shape: Shape):
        """Get the shape lane, row and column"""
        for lane_id, lane in self._grid.items():
            for row, col in lane.items():
                if shape in col:
                    # get row number
                    row_number = int(row.replace("row", ""))
                    return lane_id, row_number, col.index(shape) + 1
        return None, None, None

    def add_shape_to_lane(self, lane_id: str, row_number: int, current_shape: Shape):
        """Add the shape to the lane"""
        if lane_id is not None:
            col_number = self.get_next_column(lane_id, row_number)
            # col_number = self.get_next_empty_column(lane_id, row_number)
            Helper.printc(
                f"            ### {lane_id=}, {row_number=}, {col_number=}",
                33,
                show_level="layout_grid",
            )
            self.add_shape_to_lane_rowcolumn(
                lane_id, row_number, col_number, current_shape
            )
        else:
            raise ValueError("lane_id must be provided")

    def add_shape_to_same_lane(self, previous_shape: Shape, current_shape: Shape):
        """Add the shape to the same lane"""
        lane_id, row_number, _ = self.get_shape_lane_rowcolumn(previous_shape)

        if lane_id is not None:
            col_number = self.get_next_column(lane_id, row_number)

            self.add_shape_to_lane_rowcolumn(
                lane_id, row_number, col_number, current_shape
            )

    def add_shape_to_same_lane_next_row(
        self, previous_shape: Shape, current_shape: Shape
    ):
        """Add the shape to the same lane next row"""
        lane_id, row_number, _ = self.get_shape_lane_rowcolumn(previous_shape)
        if lane_id is not None:
            col_number = self.get_next_column(lane_id, row_number)

            next_row_number = row_number + 1
            while True:
                if self.is_column_empty(lane_id, next_row_number, col_number):
                    self.add_shape_to_lane_rowcolumn(
                        lane_id, next_row_number, col_number, current_shape
                    )
                    break

                next_row_number += 1

    def get_next_column(self, lane_id: str, row_number: int) -> int:
        """Get the next column"""
        # get next None column
        if lane_id not in self._grid:
            return 1

        # find out the last column that is not None
        max_columns = self.get_max_column_count()

        row_key = f"row{row_number}"
        if row_key not in self._grid[lane_id]:
            return 1

        # Find the last occupied column in this row
        col_array = self._grid[lane_id][row_key]

        last_column = 0
        # row_number = f"row{row_number}"
        # for col_number in range(max_columns + 1):
        #     for row, col in self._grid[lane_id].items():
        #         if row == row_number and col[col_number - 1] is not None:
        #             last_column = col_number
        for idx, item in enumerate(col_array):
            if item is not None:
                last_column = idx + 1

        return last_column + 1

    def format_itemX(self, item, repeat: bool = False):
        # sourcery skip: assign-if-exp, simplify-boolean-comparison
        """Format the item"""
        # get the first 20 characters from item
        item = str(item)[:20]
        fixed_length = 20

        if repeat is False:
            spaces = " " * fixed_length
        else:
            spaces = item * fixed_length

        if item == "None":
            return f"{spaces}|"

        return item + spaces[: fixed_length - len(item)] + "|"

    def format_item(self, item, repeat: bool = False):
        # sourcery skip: assign-if-exp, simplify-boolean-comparison
        """Format the item"""
        # get the first 20 characters from item
        item = str(item)[:20]
        fixed_length = 20

        if repeat is False:
            spaces = " " * fixed_length
        else:
            spaces = item * fixed_length

        if item == "None":
            return f"{spaces}"

        return item + spaces[: fixed_length - len(item)]

    def get_max_column_count(self):
        """Get the max number of columns"""
        max_columns = 0
        # calculate max number of columns
        for _, lane in self._grid.items():
            for _, col in lane.items():
                if len(col) > max_columns:
                    max_columns = len(col)
        return max_columns

    def get_lane_row_count(self, lane_id: str):
        """Get the lane row count"""
        return len(self._grid[lane_id])

    def print_headerX(
        self,
    ):
        """Print the header"""
        max_columns = self.get_max_column_count()
        # calculate max number of columns
        for _, lane in self._grid.items():
            for _, col in lane.items():
                if len(col) > max_columns:
                    max_columns = len(col)

        for _, lane in self._grid.items():
            Helper.printc(
                self.format_item(r"ROW \ COL"),
                end="",
                color=33,
                show_level="layout_grid",
            )
            for i in range(max_columns):
                Helper.printc(
                    f"{self.format_item(i+1)}",
                    end="",
                    color=33,
                    show_level="layout_grid",
                )
            Helper.printc("", show_level="layout_grid")
            for _ in range(max_columns + 1):
                Helper.printc(
                    self.format_item("-", True),
                    end="",
                    color=33,
                    show_level="layout_grid",
                )
            Helper.printc("", show_level="layout_grid")
            break

    def print_header(self, table: Table):
        max_columns = self.get_max_column_count()
        for _, lane in self._grid.items():
            for _, col in lane.items():
                if len(col) > max_columns:
                    max_columns = len(col)

        for _, lane in self._grid.items():
            table.add_column("ROW \ COL")
            for i in range(max_columns):
                table.add_column(self.format_item(i + 1))
            break

    def print_grid(self):
        if Helper.show_layout_grid is True:
            for lane_id, lane in self._grid.items():
                Helper.printc(f"{lane_id=}", color=33, show_level="layout_grid")
                console = Console()
                table = Table(
                    show_header=True, header_style="bold magenta", show_lines=True
                )
                self.print_header(table)
                for row_number, col in lane.items():
                    row_data = [self.format_item(row_number)]
                    for item in col:
                        if item is not None:
                            row_data.append(self.format_item(item.name))
                        else:
                            row_data.append(self.format_item("None"))

                    table.add_row(*row_data)

                console.print(table)