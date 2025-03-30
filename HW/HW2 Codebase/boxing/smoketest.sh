#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 22:07:36 2025

@author: viroop
"""

#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Boxer Management
#
##########################################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer: $name (Weight: $weight, Height: $height, Reach: $reach, Age: $age)..."
  curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
    -d "{\"name\": \"$name\", \"weight\": $weight, \"height\": $height, \"reach\": $reach, \"age\": $age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer created successfully."
  else
    echo "Failed to create boxer."
    exit 1
  fi
}

delete_boxer_by_id() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  name=$1

  echo "Getting boxer by name: $name..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name?name=$(echo $name | sed 's/ /%20/g')")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name: $name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name."
    exit 1
  fi
}

get_boxer_leaderboard() {
  sort_by=$1
  echo "Getting boxer leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/get-leaderboard?sort_by=$sort_by")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer leaderboard."
    exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

enter_boxer_into_ring() {
  boxer_id=$1

  echo "Entering boxer with ID ($boxer_id) into the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-boxer-into-ring/$boxer_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer with ID ($boxer_id) entered the ring successfully."
  else
    echo "Failed to enter boxer into the ring."
    exit 1
  fi
}

get_boxers_in_ring() {
  echo "Getting boxers currently in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers-in-ring")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers in ring retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON (in ring):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve boxers in the ring."
    exit 1
  fi
}

clear_ring() {
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-ring")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear the ring."
    exit 1
  fi
}

simulate_fight() {
  echo "Simulating fight between boxers in the ring..."
  response=$(curl -s -X POST "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight simulation successful."
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to simulate fight."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/playlist.db < sql/init_db.sql

# Health and DB checks
check_health
check_db

# Create boxers
create_boxer "Boxer 1" 172 181 71.5 27
create_boxer "Boxer 1" 170 180 70 25
create_boxer "Boxer 2" 188 179 73.2 30
create_boxer "Boxer 3" 134 170 68.9 24
create_boxer "Boxer 4" 205 185 76.1 32
create_boxer "Boxer 5" 145 174 69.4 22

delete_boxer_by_id 5

get_boxer_by_name "Boxer 1"
get_boxer_by_id 1

get_boxer_by_id 999

get_boxer_leaderboard wins

enter_boxer_into_ring 1
enter_boxer_into_ring 2
enter_boxer_into_ring 3

simulate_fight  

clear_ring

enter_boxer_into_ring 1
enter_boxer_into_ring 2

simulate_fight

clear_ring

get_boxers_in_ring
