import pytest
from thermometers_mip_solver import ThermometerPuzzle, ThermometersSolver


class TestThermometersSolver:
    """Test cases for the ThermometersSolver class."""

    def test_solver_creation(self):
        """Test basic solver creation."""
        puzzle = ThermometerPuzzle(
            row_sums=[1, 1],
            col_sums=[1, 1],
            thermometer_waypoints=[
                [(0, 0), (0, 1)],
                [(1, 1), (1, 0)]
            ]
        )
        
        solver = ThermometersSolver(puzzle)
        assert solver.puzzle == puzzle
        assert solver.solver is not None
        assert len(solver.cell_vars) == 4  # 2x2 grid

    def test_invalid_puzzle_type(self):
        """Test that invalid puzzle type raises ValueError."""
        with pytest.raises(ValueError, match="Puzzle must be a ThermometerPuzzle instance"):
            ThermometersSolver("not a puzzle")

    def test_solve_simple_puzzle(self):
        """Test solving a simple 2x2 puzzle."""
        puzzle = ThermometerPuzzle(
            row_sums=[1, 1],
            col_sums=[1, 1],
            thermometer_waypoints=[
                [(0, 0), (0, 1)],
                [(1, 1), (1, 0)]
            ]
        )
        
        solver = ThermometersSolver(puzzle)
        solution = solver.solve()
        
        assert solution is not None
        assert len(solution) == 2  # Should fill 2 cells total
        assert solver.validate_solution(solution)
        assert puzzle.is_valid_solution(solution)

    def test_solve_complex_puzzle(self):
        """Test solving the complex example puzzle."""
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
        
        solver = ThermometersSolver(puzzle)
        solution = solver.solve()
        
        assert solution is not None
        assert len(solution) == 7  # Should fill 7 cells total
        assert solver.validate_solution(solution)
        
        # Should match the known solution
        expected = {(0, 3), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (3, 3)}
        assert solution == expected

    def test_no_solution_puzzle(self):
        """Test puzzle with no solution."""
        # Create a puzzle that is unsolvable
        # Two 2-cell thermometers in a 2x2 grid with [1,1] row/col sums
        puzzle = ThermometerPuzzle(
            row_sums=[1, 1],
            col_sums=[1, 1],
            thermometer_waypoints=[
                [(0, 0), (1, 0)],
                [(0, 1), (1, 1)]
            ]
        )
        
        solver = ThermometersSolver(puzzle)
        solution = solver.solve()
        
        # This puzzle should have no solution due to thermometer constraints
        assert solution is None

    def test_solver_info(self):
        """Test getting solver information."""
        puzzle = ThermometerPuzzle(
            row_sums=[1, 1],
            col_sums=[1, 1],
            thermometer_waypoints=[
                [(0, 0), (1, 0)], [(0, 1), (1, 1)]
            ]
        )
        
        solver = ThermometersSolver(puzzle)
        info = solver.get_solver_info()
        
        assert 'solver_type' in info
        assert 'num_variables' in info
        assert 'num_constraints' in info
        assert 'grid_size' in info
        assert 'num_thermometers' in info
        assert 'total_cells' in info
        
        assert info['num_variables'] == 4  # 2x2 grid
        assert info['grid_size'] == '2x2'
        assert info['num_thermometers'] == 2
        assert info['total_cells'] == 4

    def test_solve_curved_4x4_puzzle(self):
        """Test solving the curved 4x4 example puzzle."""
        puzzle = ThermometerPuzzle(
            row_sums=[3, 1, 2, 1],
            col_sums=[1, 2, 3, 1],
            thermometer_waypoints=[
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(2, 2), (0, 2), (0, 3), (2, 3)],
                [(3, 1), (2, 1), (2, 0), (3, 0)],
                [(3, 3), (3, 2)],
            ]
        )
        
        solver = ThermometersSolver(puzzle)
        solution = solver.solve()
        
        assert solution is not None
        assert len(solution) == 7  # Should fill 7 cells total
        assert solver.validate_solution(solution)
        
        # Should match the known solution
        expected = {(0, 0), (0, 2), (0, 3), (1, 2), (2, 1), (2, 2), (3, 1)}
        assert solution == expected

    def test_solve_5x5_missing_values_example(self):
        """Test solver with the 5x5 example from main.py that has missing constraints."""
        puzzle = ThermometerPuzzle(
            row_sums=[2, 3, None, 5, None],
            col_sums=[None, None, 1, 4, 4],
            thermometer_waypoints=[
                [(0, 0), (0, 2), (2, 2)],            # L-shaped thermometer
                [(2, 0), (1, 0), (1, 1), (2, 1)],    # ∩-shaped thermometer
                [(2, 3), (0, 3), (0, 4)],            # L-shaped thermometer
                [(3, 0), (3, 3)],                    # Straight thermometer
                [(3, 4), (1, 4)],                    # Straight thermometer
                [(4, 0), (4, 1)],                    # Straight thermometer
                [(4, 2), (4, 4)],                    # Straight thermometer
            ]
        )
        
        solver = ThermometersSolver(puzzle)
        solution = solver.solve()
        
        # Expected solution
        expected_solution = {
            (0, 3), (0, 4), (1, 0), (1, 3), (1, 4), (2, 0), (2, 3), (2, 4), 
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, 0)
        }

        assert solution == expected_solution
