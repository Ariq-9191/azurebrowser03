import tensorflow as tf

def test_tensorflow():
	# Create a simple tensor
	print("TensorFlow version:", tf.__version__)
	print("\nCreating and manipulating tensors:")
	
	# Create a tensor
	tensor = tf.constant([[1, 2], [3, 4]])
	print("Tensor:", tensor)
	
	# Perform some operations
	result = tf.add(tensor, tensor)
	print("\nResult of adding tensor to itself:", result)

if __name__ == "__main__":
	test_tensorflow()