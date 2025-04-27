# Count the number of repos found in the 'saverepos' directory
import os

def count_directories(directory_path):
    try:
        total = 0
        # List all entries in the directory
        entries = os.listdir(directory_path)

        # Filter out directories
        directories = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]

        for year in directories: 
            repos_this_year = 0
            subdirs = os.listdir(os.path.join(directory_path, year))
            subdirectories_this_year  = [entry for entry in subdirs if os.path.isdir(os.path.join(directory_path, year, entry))]
            for subdir in subdirectories_this_year:
                repos = os.listdir(os.path.join(directory_path, year, subdir))
                total += len(repos)
                repos_this_year += len(repos)

            print(f"number of repos for {year} is {repos_this_year}")

        # Return the count of directories
        return total

    except FileNotFoundError:
        print(f"The directory '{directory_path}' does not exist.")
        return 0
    except PermissionError:
        print(f"Permission denied to access the directory '{directory_path}'.")
        return 0

directory_path = '/home/yangjin/verilog-repos/saverepo'  
num_directories = count_directories(directory_path)
print(f"Number of directories in '{directory_path}': {num_directories}")
directory_path = '/home/yangjin/verilog-repos2'  
num_directories_two = count_directories(directory_path)
print(f"Number of directories in '{directory_path}': {num_directories_two}")
total = num_directories + num_directories_two
print(f"Number of directories total: {total}")

