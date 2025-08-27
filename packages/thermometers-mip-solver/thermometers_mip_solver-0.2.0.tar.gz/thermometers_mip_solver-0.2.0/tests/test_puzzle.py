import pytest
from thermometers_mip_solver import ThermometerPuzzle, Thermometer


class TestThermometer:
    """Test cases for the Thermometer class."""

    def test_basic_creation(self):
        """Test creating a basic thermometer."""
        positions = [(0, 0), (0, 1), (0, 2)]
        thermo = Thermometer(1, positions)
        
        assert thermo.id == 1
        assert thermo.positions == positions
        assert thermo.length == 3
        assert thermo.bulb_position == (0, 0)
        assert thermo.top_position == (0, 2)

    def test_single_cell_thermometer(self):
        """Test that single-cell thermometers raise ValueError."""
        with pytest.raises(ValueError, match="Thermometers must have at least 2 cells"):
            Thermometer(0, [(1, 1)])

    def test_empty_positions(self):
        """Test that empty waypoints raise ValueError."""
        with pytest.raises(ValueError, match="Thermometer must have at least one waypoint"):
            Thermometer(1, [])

    def test_duplicate_positions(self):
        """Test that duplicate positions raise ValueError."""
        with pytest.raises(ValueError, match="Thermometer cannot have duplicate positions"):
            Thermometer(1, [(0, 0), (0, 1), (0, 0)])

    def test_waypoint_expansion(self):
        """Test that waypoints are expanded correctly into full paths."""
        # Horizontal expansion (left to right)
        thermo1 = Thermometer(1, [(0, 0), (0, 2)])
        assert thermo1.positions == [(0, 0), (0, 1), (0, 2)]
        
        # Horizontal expansion (right to left)
        thermo2 = Thermometer(2, [(0, 3), (0, 1)])
        assert thermo2.positions == [(0, 3), (0, 2), (0, 1)]
        
        # Vertical expansion (top to bottom)
        thermo3 = Thermometer(3, [(0, 0), (2, 0)])
        assert thermo3.positions == [(0, 0), (1, 0), (2, 0)]
        
        # Vertical expansion (bottom to top)
        thermo4 = Thermometer(4, [(3, 0), (1, 0)])
        assert thermo4.positions == [(3, 0), (2, 0), (1, 0)]
        
        # L-shaped path (vertical then horizontal)
        thermo5 = Thermometer(5, [(2, 0), (0, 0), (0, 3)])
        assert thermo5.positions == [(2, 0), (1, 0), (0, 0), (0, 1), (0, 2), (0, 3)]
        
        # Same waypoint twice (no expansion needed)
        thermo6 = Thermometer(6, [(1, 1), (1, 1)])
        assert thermo6.positions == [(1, 1)]

    def test_invalid_diagonal_waypoints(self):
        """Test that diagonal waypoints raise ValueError."""
        # Diagonal waypoints are not allowed - thermometers can only move in cardinal directions
        with pytest.raises(ValueError, match="Waypoints .* are not horizontally or vertically aligned"):
            Thermometer(1, [(0, 0), (1, 1)])
        
        # Another diagonal case
        with pytest.raises(ValueError, match="Waypoints .* are not horizontally or vertically aligned"):
            Thermometer(2, [(2, 3), (1, 4)])

    def test_valid_adjacent_positions(self):
        """Test various valid adjacent position patterns."""
        # Horizontal
        Thermometer(1, [(0, 0), (0, 1), (0, 2)])
        
        # Vertical
        Thermometer(2, [(2, 0), (1, 0), (0, 0)])
        
        # L-shaped
        Thermometer(3, [(2, 0), (1, 0), (1, 1), (1, 2)])
        
        # Snake pattern
        Thermometer(4, [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)])

    def test_valid_fill_states(self):
        """Test validation of thermometer fill states."""
        thermo = Thermometer(1, [(0, 0), (0, 1), (0, 2), (0, 3)])
        
        # Valid states: continuous from bulb
        assert thermo.is_valid_fill_state(set())  # Empty
        assert thermo.is_valid_fill_state({(0, 0)})  # Bulb only
        assert thermo.is_valid_fill_state({(0, 0), (0, 1)})  # First two
        assert thermo.is_valid_fill_state({(0, 0), (0, 1), (0, 2)})  # First three
        assert thermo.is_valid_fill_state({(0, 0), (0, 1), (0, 2), (0, 3)})  # All

    def test_invalid_fill_states(self):
        """Test invalid thermometer fill states."""
        thermo = Thermometer(1, [(0, 0), (0, 1), (0, 2), (0, 3)])
        
        # Invalid states
        assert not thermo.is_valid_fill_state({(0, 1)})  # Skip bulb
        assert not thermo.is_valid_fill_state({(0, 2)})  # Skip bulb and first
        assert not thermo.is_valid_fill_state({(0, 3)})  # Only top
        assert not thermo.is_valid_fill_state({(0, 0), (0, 2)})  # Gap in middle
        assert not thermo.is_valid_fill_state({(0, 0), (0, 1), (0, 3)})  # Gap at end

    def test_fill_state_with_unrelated_positions(self):
        """Test that unrelated filled positions don't affect validation."""
        thermo = Thermometer(1, [(0, 0), (0, 1)])
        
        # Valid fill with extra unrelated positions
        filled = {(0, 0), (1, 1), (2, 2)}  # Only (0,0) is from this thermometer
        assert thermo.is_valid_fill_state(filled)

    def test_repr(self):
        """Test string representation."""
        thermo = Thermometer(5, [(1, 2), (1, 3)])
        assert repr(thermo) == "Thermometer(5, [(1, 2), (1, 3)])"


class TestThermometerPuzzle:
    """Test cases for the ThermometerPuzzle class."""

    def test_basic_creation(self):
        """Test creating a basic puzzle."""
        puzzle = ThermometerPuzzle(
            row_sums=[1, 1],
            col_sums=[1, 1],
            thermometer_waypoints=[
                [(0, 0), (0, 1)],
                [(1, 1), (1, 0)]
            ]
        )
        
        assert puzzle.height == 2
        assert puzzle.width == 2
        assert len(puzzle.thermometers) == 2
        assert puzzle.row_sums == [1, 1]
        assert puzzle.col_sums == [1, 1]

    def test_empty_sums(self):
        """Test that empty row or column sums raise ValueError."""
        with pytest.raises(ValueError, match="Row and column sums cannot be empty"):
            ThermometerPuzzle([], [1], [[(0, 0)]])
        
        with pytest.raises(ValueError, match="Row and column sums cannot be empty"):
            ThermometerPuzzle([1], [], [[(0, 0)]])

    def test_negative_sums(self):
        """Test that negative sums raise ValueError."""
        with pytest.raises(ValueError, match="All sums must be non-negative"):
            ThermometerPuzzle([-1, 1], [1, 1], [[(0, 0)], [(0, 1)]])
        
        with pytest.raises(ValueError, match="All sums must be non-negative"):
            ThermometerPuzzle([1, 1], [1, -1], [[(0, 0)], [(0, 1)]])

    def test_mismatched_total_sums(self):
        """Test that mismatched row and column sum totals raise ValueError."""
        with pytest.raises(ValueError, match="Sum of row sums must equal sum of column sums"):
            ThermometerPuzzle([2], [1], [[(0, 0)]])

    def test_row_sum_exceeds_width(self):
        """Test that row sum exceeding grid width raises ValueError."""
        # Note: Need matching total sums first, then the row sum check will trigger
        with pytest.raises(ValueError, match="Row sum cannot exceed grid width"):
            ThermometerPuzzle([6], [3, 3], [[(0, 0)], [(0, 1)]])

    def test_col_sum_exceeds_height(self):
        """Test that column sum exceeding grid height raises ValueError."""
        # Note: Need matching total sums first, then the col sum check will trigger
        with pytest.raises(ValueError, match="Column sum cannot exceed grid height"):
            ThermometerPuzzle([2], [2, 0], [[(0, 0)], [(0, 1)]])  # height=1, but col sum 2 > 1

    def test_no_thermometer_waypoints(self):
        """Test that no thermometer waypoints raises ValueError."""
        with pytest.raises(ValueError, match="At least one thermometer waypoints list must be provided"):
            ThermometerPuzzle([1], [1], [])

    def test_empty_thermometer_waypoints(self):
        """Test that empty thermometer waypoints raises ValueError."""
        with pytest.raises(ValueError, match="Thermometer waypoints 0 is empty"):
            ThermometerPuzzle([1], [1], [[]])

    def test_position_out_of_bounds(self):
        """Test that out-of-bounds positions raise ValueError."""
        with pytest.raises(ValueError, match="Position .* outside grid bounds"):
            ThermometerPuzzle([1, 1], [2], [[(0, 2), (1, 2)]])
        
        # Negative position
        with pytest.raises(ValueError, match="Position .* outside grid bounds"):
            ThermometerPuzzle([1, 1], [1, 1], [[(0, 0), (1, 0)], [(-1, 0), (-1, 1)]])

    def test_overlapping_thermometers(self):
        """Test that overlapping thermometers raise ValueError."""
        with pytest.raises(ValueError, match="Position .* covered by multiple thermometers"):
            ThermometerPuzzle(
                [2, 0], [1, 1],
                [
                    [(0, 0), (0, 1)],
                    [(0, 1), (1, 1)]
                ]  # Both cover (0, 1)
            )

    def test_incomplete_grid_coverage(self):
        """Test that incomplete grid coverage raises ValueError."""
        with pytest.raises(ValueError, match="Grid not completely filled"):
            ThermometerPuzzle(
                [1, 1], [1, 1],
                [[(0, 0), (1, 0)]]  # Only covers 2 of 4 positions
            )

    def test_valid_solution_checking(self):
        """Test solution validation."""
        puzzle = ThermometerPuzzle(
            row_sums=[1, 2],
            col_sums=[2, 1],
            thermometer_waypoints=[
                [(1, 0), (0, 0)],  # Vertical thermometer
                [(1, 1), (0, 1)]   # Another vertical thermometer
            ]
        )
        
        # Valid solution: fill both bulbs and one top
        valid_solution = {(1, 0), (0, 0), (1, 1)}
        assert puzzle.is_valid_solution(valid_solution)
        
        # Invalid: wrong row sums
        invalid_row_sums = {(0, 0), (1, 1)} 
        assert not puzzle.is_valid_solution(invalid_row_sums)
        
        # Invalid: wrong column sums  
        invalid_col_sums = {(1, 0), (1, 1)}
        assert not puzzle.is_valid_solution(invalid_col_sums)
        
        # Invalid: thermometer fill violation (fill top without bulb)
        invalid_thermo = {(0, 0), (1, 1)}
        assert not puzzle.is_valid_solution(invalid_thermo)

    def test_get_thermometer_at(self):
        """Test finding thermometer at specific position."""
        puzzle = ThermometerPuzzle(
            [2], [1, 1],
            [[(0, 0), (0, 1)]]
        )
        
        thermo = puzzle.get_thermometer_at((0, 0))
        assert thermo is not None
        assert thermo.id == 0
        
        thermo = puzzle.get_thermometer_at((0, 1))
        assert thermo is not None  
        assert thermo.id == 0
        
        # Position not in puzzle
        assert puzzle.get_thermometer_at((1, 0)) is None

    def test_get_position_to_thermometer_map(self):
        """Test getting position to thermometer mapping."""
        puzzle = ThermometerPuzzle(
            [1, 1], [1, 1],
            [[(0, 0), (0, 1)], [(1, 0), (1, 1)]]
        )
        
        pos_map = puzzle.get_position_to_thermometer_map()
        
        assert len(pos_map) == 4
        assert pos_map[(0, 0)].id == 0
        assert pos_map[(0, 1)].id == 0
        assert pos_map[(1, 0)].id == 1
        assert pos_map[(1, 1)].id == 1

    def test_complex_puzzle(self):
        """Test with the real example."""
        puzzle = ThermometerPuzzle(
            row_sums=[1, 3, 2, 1],
            col_sums=[1, 2, 2, 2],
            thermometer_waypoints=[
                [(0, 2), (0, 1), (0, 0)],  
                [(0, 3), (1, 3)],
                [(1, 0), (2, 0)],
                [(1, 1), (1, 2)],
                [(2, 1), (2, 2), (2, 3)],
                [(3, 1), (3, 0)],
                [(3, 3), (3, 2)]
            ]
        )
        
        assert puzzle.height == 4
        assert puzzle.width == 4
        assert len(puzzle.thermometers) == 7
        
        # Test known valid solution
        solution = {(0, 3), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (3, 3)}
        assert puzzle.is_valid_solution(solution)

    def test_repr(self):
        """Test string representation."""
        puzzle = ThermometerPuzzle(
            [1, 1], [1, 1],
            [[(0, 0), (0, 1)], [(1, 0), (1, 1)]]
        )
        assert repr(puzzle) == "ThermometerPuzzle(2x2, 2 thermometers)"

    def test_missing_values_creation_and_validation(self):
        """Test creating a puzzle with missing row/column values."""
        # Using the example from main.py
        puzzle = ThermometerPuzzle(
            row_sums=[2, 3, None, 5, None],
            col_sums=[None, None, 1, 4, 4],
            thermometer_waypoints=[
                [(0, 0), (0, 2), (2, 2)],            # L-shaped thermometer starting in row 0
                [(2, 0), (1, 0), (1, 1), (2, 1)],    # ∩-shaped thermometer starting in row 2
                [(2, 3), (0, 3), (0, 4)],            # L-shaped thermometer starting in row 2
                [(3, 0), (3, 3)],                    # Straight thermometer starting in row 3
                [(3, 4), (1, 4)],                    # Straight thermometer starting in row 3
                [(4, 0), (4, 1)],                    # Straight thermometer starting in row 4
                [(4, 2), (4, 4)],                    # Straight thermometer starting in row 4
            ]
        )
        
        assert puzzle.height == 5
        assert puzzle.width == 5
        assert puzzle.row_sums == [2, 3, None, 5, None]
        assert puzzle.col_sums == [None, None, 1, 4, 4]

        # Validate solution
        solution = {
            (0, 3), (0, 4), (1, 0), (1, 3), (1, 4), (2, 0), (2, 3), (2, 4), 
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, 0)
        }
        
        assert puzzle.is_valid_solution(solution)

class TestThermometerIntegration:
    """Integration tests for Thermometer and ThermometerPuzzle working together."""

    def test_thermometer_properties_in_puzzle(self):
        """Test that thermometer properties work correctly within puzzle context."""
        puzzle = ThermometerPuzzle(
            [2, 2], [2, 2],
            [[(0, 0), (1, 0), (1, 1), (0,1)]]  # Single U-shaped thermometer in 2x2 grid
        )
        
        thermo = puzzle.thermometers[0]
        assert thermo.length == 4
        assert thermo.bulb_position == (0, 0)
        assert thermo.top_position == (0, 1)
        
        # Test valid partial fills
        assert thermo.is_valid_fill_state({(0, 0)})  # Bulb only
        assert thermo.is_valid_fill_state({(0, 0), (1, 0)})  # First two
        assert thermo.is_valid_fill_state({(0, 0), (1, 0), (1, 1), (0, 1)})  # All cells

        # Test invalid fills
        assert not thermo.is_valid_fill_state({(1, 0)})  # Skip bulb
        assert not thermo.is_valid_fill_state({(0, 1)})  # Only top

    def test_puzzle_validation_catches_thermometer_errors(self):
        """Test that puzzle validation catches thermometer creation errors."""
        # Diagonal waypoints should be caught during thermometer creation
        with pytest.raises(ValueError, match="Waypoints .* are not horizontally or vertically aligned"):
            ThermometerPuzzle(
                [1, 1], [1, 1],
                [[(0, 0), (1, 1)]]  # Diagonal waypoints
            )
