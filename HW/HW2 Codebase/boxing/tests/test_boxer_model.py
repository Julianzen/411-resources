from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the catalog.

    """
    create_boxer(name="Boxer Name", weight=140, height=177, reach=20.2,age=30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age, weight_class)
        VALUES (?, ?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 140, 177, 20.2, 30, "MIDDLEWEIGHT")

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate parameters.

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name, boxers.weight, boxers.height, boxers.age")

    with pytest.raises(ValueError, match="Boxer with name 'Boxer Name', height '140', reach '20.2', and age 30 already exists."):
        create_boxer(name="Boxer Name", weight=140, height=177, reach=20.2,age=30)

def test_create_boxer_invalid_weight():
    """Test error when trying to create a boxer with an invalid weight (e.g., negative weight)

    """
    with pytest.raises(ValueError, match=r"Invalid weight: -180 \(must be an integer greater than or equal to 125\)."):
        
        create_boxer(name="Boxer Name", weight=-140, height=177, reach=20.2,age=30)

    with pytest.raises(ValueError, match=r"Invalid weight: invalid \(must be an integer greater than or equal to 125\)."):
        
        create_boxer(name="Boxer Name", weight="invalid", height=177, reach=20.2,age=30)


def test_create_boxer_invalid_height():
    """Test error when trying to create a boxer with an invalid height (e.g., non-negative).

    """
    with pytest.raises(ValueError, match=r"Invalid height: -177 \(must be a positive integer\)."):
       
        create_boxer(name="Boxer Name", weight=140, height=-177, reach=20.2,age=30)
        

    with pytest.raises(ValueError, match=r"Invalid height: -177 \(must be a positive integer\)."):
        create_boxer(name="Boxer Name", weight=140, height="invalid", reach=20.2,age=30)

def test_create_boxer_invalid_reach():
    """Test error when trying to create a boxer with an invalid reach (e.g., less than 0 or non-integer).

    """
    with pytest.raises(ValueError, match=r"Invalid reach: -10 \(must be an integer greater than or equal to 0\)."):
        create_boxer(name="Boxer Name", weight=140, height=177, reach = -10, age = 30)

    with pytest.raises(ValueError, match=r"Invalid reach: invalid \(must be an integer greater than or equal to 0\)."):
        create_boxer(name="Boxer Name", weight=140, height=177, reach = "invalid", age = 30)
        
def test_create_boxer_invalid_age():
    """Test error when trying to create a boxer with an invalid age (e.g., less than 18 or greater than 40 or non-integer).

    """
    with pytest.raises(ValueError, match=r"Invalid age: -10 \(must be an integer less than or equal to 40 and greater than or equal to 18\)."):
        create_boxer(name="Boxer Name", weight=140, height=177, reach = 20, age = -10)
    
    with pytest.raises(ValueError, match=r"Invalid age: 50 \(must be an integer less than or equal to 40 and greater than or equal to 18\)."):
        create_boxer(name="Boxer Name", weight=140, height=177, reach = 20, age = 50)

    with pytest.raises(ValueError, match=r"Invalid age: invalid \(must be an integer less than or equal to 40 and greater than or equal to 18\)."):
        create_boxer(name="Boxer Name", weight=140, height=177, reach = 20, age = "invalid")
        
        
def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the catalog by boxer ID.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent boxer.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Get Boxer
#
######################################################


def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id.

        unsure about the False value

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 140, 177, 20.2,30, False)

    result = get_boxer_by_id(1)

    expected_result = Boxer(1, "Boxer Name", 140, 177, 20.2,30)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)

def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name.

        unsure about the False value

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 140, 177, 20.2,30, False)

    result = get_boxer_by_name("Boxer Name")

    expected_result = Boxer(1, "Boxer Name", 140, 177, 20.2,30)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_bad_name(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with name Big Fart not found"):
        get_boxer_by_name("Big Fart")



def test_get_leaderboard_sorted_by_wins(mock_cursor):
    """Test getting the leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (1, "Boxer A", 150, 180, 75.5, 28, 30, 25, 0.8333),
        (2, "Boxer B", 160, 185, 78.0, 31, 40, 30, 0.7500)
    ]

    result = get_leaderboard(sort_by="wins")

    expected_result = [
        {'id': 1, 'name': "Boxer A", 'weight': 150, 'height': 180, 'reach': 75.5, 'age': 28,
         'weight_class': get_weight_class(150), 'fights': 30, 'wins': 25, 'win_pct': 83.3},
        {'id': 2, 'name': "Boxer B", 'weight': 160, 'height': 185, 'reach': 78.0, 'age': 31,
         'weight_class': get_weight_class(160), 'fights': 40, 'wins': 30, 'win_pct': 75.0}
    ]

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace(
        """
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0 ORDER BY wins DESC
        """
    )
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test error when invalid sort_by parameter is used."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_metric"):
        get_leaderboard(sort_by="invalid_metric")



def test_get_weight_class(mock_cursor):
    """Test for correct weight class classification."""
    result = get_weight_class(150)
    expected_result = 'LIGHTWEIGHT'
    assert result == expected_result, f"Expected {expected_result}, got {result}"

def test_get_weight_class_invalid_weight(mock_cursor):
    """Test for invalid weight classification."""
    with pytest.raises(ValueError, match="Invalid weight: 124. Weight must be at least 125."):
        get_weight_class(124)



######################################################
#
#    Boxer Win count
#
######################################################


def test_update_boxer_stats(mock_cursor):
    """Test updating the win count of a boxer.

    """
    mock_cursor.fetchone.return_value = True

    boxer_id = 1
    update_boxer_stats(boxer_id)

    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    expected_arguments = (boxer_id,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."