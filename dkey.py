import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.tree import _tree


def load_data(file_path):
	"""Load CSV data into a DataFrame."""
	return pd.read_csv(file_path)


def preprocess_data(df):
	"""Preprocess the data for tree generation."""
	# Convert categorical columns to numerical
	feature_cols = df.columns[2:]  # Assuming first two columns are ID and Name
	X = pd.get_dummies(df[feature_cols])
	y = df['Name']  # Assuming 'Name' identifies each specimen
	return X, y, feature_cols


def build_tree(X, y):
	"""Train a decision tree classifier."""
	tree = DecisionTreeClassifier(criterion="entropy", max_leaf_nodes=len(y))
	tree.fit(X, y)
	return tree

def generate_old_dichotomous_key(tree, feature_names):
	"""Generate a text-based dichotomous key."""
	tree_rules = export_text(tree, feature_names=feature_names)
	return tree_rules

from sklearn.tree import _tree

def format_dichotomous_key(tree, feature_names):
	"""Format the decision tree into a custom dichotomous key."""
	tree_ = tree.tree_

	print("features", feature_names)

	def process_feature_names(feature_names):
		"""
		Convert feature names into human-readable strings and store them in a dictionary.
		E.g., "Attribute1_No" → "Attribute1 is No"
		"""
		processed_names = {}
		# Convert to list
		feature_names_list = feature_names.tolist()
		for feature in feature_names_list:
			print("hello", feature)
			if "_" in feature:  # Check if underscore is present in the feature name
				# Split the feature name into parts
				attribute, value = feature.split("_", 1)
				# Format the string as "Attribute is Value"
				human_readable = f"{attribute} is {value}"
			else:
				# If no underscore, keep the name as is
				human_readable = feature

			# Store the mapping in the dictionary
			processed_names[feature] = human_readable

		print(processed_names)  # Debugging line to see the result
		return processed_names

	naming_dict = process_feature_names(feature_names)

	# We need to store steps with their corresponding step numbers
	steps = []

	def recurse(node, depth):
		nonlocal step_counter
		current_step = step_counter
		step_counter += 1

		# Initialize condition to prevent referencing before assignment
		# condition = ""

		if tree_.feature[node] != _tree.TREE_UNDEFINED:
			# Internal node
			feature_name = feature_names[tree_.feature[node]]  # Get the feature name
			threshold = tree_.threshold[node]  # Get the threshold for the condition
			condition = f"{feature_name} <= {threshold:.2f}" if tree_.impurity[node] != 0 else f"{feature_name} > {threshold:.2f}"
			# Check if feature is categorical or numeric
			if "_" in feature_name:  # Categorical values like Size_Large, Sticky Cap_No
				attribute, value = feature_name.split("_", 1)
				print("inside", feature_name, attribute, value)
				if value == "No":
					# If it's a "No" (e.g., Sticky Cap_No), say "Is Lack of X True?"
					condition = f"Is {attribute} True?"
				elif value == "Yes":
					# If it's a "Yes" (e.g., Sticky Cap_Yes), say "Is X True?"
					condition = f"Is {attribute} False?"
				else:
					condition = f"Is {attribute} {value}?"
			else:
				# Numeric conditions (e.g., "Spore Length Max <= 10.50")
				if tree_.impurity[node] != 0:
					condition = f"{feature_name} <= {threshold:.2f}"
				else:
					condition = f"{feature_name} > {threshold:.2f}"

			# Record the step for the condition (TRUE/FALSE check)
			yes_step = step_counter
			recurse(tree_.children_left[node], depth + 1)
			
			no_step = step_counter
			recurse(tree_.children_right[node], depth + 1)

			# Add the formatted condition to the steps list
			steps.append((current_step, f"{current_step}: {condition}"))
			steps.append((current_step, f"   Yes → Go to Step {yes_step} | No → Go to Step {no_step}"))

		else:
			# Leaf node
			values = tree_.value[node].flatten()
			specimen = ", ".join(
				f"{label}"
				for label, count in zip(tree.classes_, values) if count > 0
			)
			steps.append((current_step, f"{current_step}: Identify as {specimen}"))

	step_counter = 1  # Start step numbering from 1
	recurse(0, 1)

	# Sort steps by their step numbers to ensure order
	steps.sort(key=lambda x: x[0])

	# Format the sorted steps
	key = "\n".join(step[1] for step in steps)
	return key