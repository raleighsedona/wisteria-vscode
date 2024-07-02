import argparse


class Generation:
    def __init__(self, grid: list, rows: int, columns: int) -> None:
        self.grid = grid
        self.rows = rows
        self.columns = columns
    
    def __str__(self) -> str:
        generation = ""

        for i in range(self.rows):
            for j in range(self.columns):
                if (self.grid[i][j] == 0):
                    generation += "-"
                else:
                    generation += "#"
            generation += "\n"

        return generation


def get_next_generation(generation: Generation) -> tuple[Generation, bool]:
    """Get the next generation in Conway's Game of Life.

    Keyword arguments:
    generation -- the current generation of cells
    """
    alive = False
    rows = generation.rows
    cols = generation.columns
    curr_generation = generation.grid
    next_generation = get_empty_grid(rows, cols)

    # Iterate over every cell
    for row in range(rows):
        for col in range(cols):

            # Count the neighboring cells that are alive
            neighbors = count_living_neighbors(generation, row, col)

            # Determine if the current cell is alive in the next generation
            if ((curr_generation[row][col] == 1 and neighbors < 2) or
                (curr_generation[row][col] == 1 and neighbors > 3)):
                next_generation[row][col] = 0

            elif (curr_generation[row][col] == 0 and neighbors == 3):
                next_generation[row][col] = 1

            else:
                next_generation[row][col] = curr_generation[row][col]

            # Determine if there is at least one living cell in the next generation
            if (not alive and next_generation[row][col] == 1):
                alive = True

    return Generation(next_generation, rows, cols), alive


def count_living_neighbors(gen: Generation, row: int, col: int) -> int:
    """Count the number alive cells neighboring the current cell.

    Keyword arguments:
    gen -- the current generation of cells
    row -- the row of the current cell
    col -- the column of the current cell
    """
    neighbors = 0

    # Add each neighbor's value to the living neighbor count
    for i in range(-1, 2):
        for j in range(-1, 2):
            if ((row + i >= 0 and row + i < gen.rows) and (col + j >= 0 and col + j < gen.columns)):
                neighbors += gen.grid[row + i][col + j]

    # Subtract the current cell from the count
    neighbors -= gen.grid[row][col]
    
    return neighbors


def get_empty_grid(rows: int, cols: int) -> list:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def populate_living_cells(grid: list, cells: list) -> list:
    for (x, y) in cells:
        grid[x][y] = 1
    
    return grid


def try_create_generation_from_file(file_path) -> Generation:
    """Attempt to create a Generation object from a file.

    Creates a new Generation object given the starting pattern from
    the specified file. Exits the program if given bad data.

    Keyword arguments:
    file_path -- the path to the file containing pattern data
    """
    try:
        with open(file_path, 'r') as file:
            metadata, points = read_pattern(file)
            rows, cols = process_metadata(metadata)
            points = process_points(points)
            grid = populate_living_cells(get_empty_grid(rows, cols), points)

        return Generation(grid, rows, cols)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")
        exit(1)


def read_pattern(file) -> tuple[list, list]:
    metadata_lines = []
    points_lines = []
    metadata_processed = False

    for line in file:
        stripped_line = line.strip()
        if stripped_line == '---':
            metadata_processed = True
            continue
        
        if not metadata_processed:
            metadata_lines.append(stripped_line)
        else:
            points_lines.append(stripped_line)

    if not metadata_processed:
        print("Error: Metadata section not properly terminated with '---'")
        return [], []

    return metadata_lines, points_lines


def process_metadata(metadata_lines) -> tuple[int, int]:
    for line in metadata_lines:
        try:
            key, value = line.split('=')
            value = int(value)
            if key == 'rows':
                rows = value
            elif key == 'cols':
                cols = value
            else:
                print(f"Error: Unrecognized metadata key '{key}' in line: '{line}'")
                exit(1)
        except ValueError:
            print(f"Error: Invalid metadata format in line: '{line}'")
            exit(1)


    return rows, cols


def process_points(points_lines) -> list:
    points = []

    for line in points_lines:
        if not line:
            continue
        try:
            x, y = map(int, line.split(','))
            points.append([x,y])
        except ValueError:
            print(f"Error: Invalid point format in line: '{line}'")
            exit(1)

    return points


def play_game(generation: Generation, max_generations: int) -> None:
    """Print to console each generation of cells in Conway's Game of Life.

    Keyword arguments:
    generation -- the starting pattern generation of cells
    max_generations -- the maximum number of generations to play through
    """
    for i in range(max_generations):
        print(str(generation))

        generation, alive = get_next_generation(generation)
        if (not alive):
            break


def main():
    parser = argparse.ArgumentParser(
            description = """Conway's Game of Life played with a given starting pattern and "
            "a maximum number of generations.""")
    
    parser.add_argument(
        'file_path',
        type = str,
        help = f"The file path of the starting pattern.")
    
    parser.add_argument(
        'max_generations',
        type = int,
        help = "The maximum number of generations to run.")
    
    args = parser.parse_args()
    play_game(try_create_generation_from_file(args.file_path), args.max_generations)


if __name__ == "__main__":
    main()
