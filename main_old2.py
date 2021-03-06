import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests
#import numpy as np

# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    # load pre-trained model
    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)
    
    # get tensors from the pre-trined model
    graph = tf.get_default_graph()
    image_input = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    vgg_layer3_out = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    vgg_layer4_out = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    vgg_layer7_out = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    return image_input, keep, vgg_layer3_out, vgg_layer4_out, vgg_layer7_out
tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer7_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer3_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    # Con 1x1 - From end to start
    # Encoder layer 7
    conv_7 = tf.layers.conv2d(vgg_layer7_out, num_classes, 1, padding='same',
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    # Decoder layer 7
    output_1 = tf.layers.conv2d_transpose(conv_7, num_classes, 4, 2, padding='same',
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    # Encoder layer 4
    conv_4 = tf.layers.conv2d(vgg_layer4_out, num_classes, 1, padding='same',
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    # Skip Connections
    decoded_1 = tf.add(output_1, conv_4)

    # Decoder upsampled layer 4
    output_2 = tf.layers.conv2d_transpose(decoded_1, num_classes, 4, 2, padding='same',
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))   
    # Encoder layer 3
    conv_3 = tf.layers.conv2d(vgg_layer3_out, num_classes, 1, padding='same',
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    # Skip Connections
    output_3 = tf.add(output_2, conv_3)
    # Decoder upsampled layer 3
    output = tf.layers.conv2d_transpose(output_3, num_classes, 16, 8, padding='same',
                                kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
    return output
tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    labels = tf.reshape(correct_label, (-1, num_classes))
    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels))
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy_loss)
    return logits, train_op, cross_entropy_loss
tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    for epoch in range(epochs):
        total_accuracy = 0
        # Reuse batch generation function
        # batch = get_batches_fn(batch_size)
        # num_examples = np.ceil(training_images / batch_size)
        for image, label in get_batches_fn(batch_size):
            feed_dict = {
                input_image: image,
                correct_label: label,
               # keep_prob: keep_prob,
                keep_prob: 0.5,
               # learning_rate: learning_rate
                learning_rate: 0.0001
            }
            _, accuracy = sess.run([train_op, cross_entropy_loss], feed_dict=feed_dict)
            total_accuracy += (accuracy * batch_size)
            print("Epoch: " + str(epoch) + "of" + str(epochs))
            print("Accuracy: {:.3f}".format(total_accuracy))
    #Saving the session
    #saver = tf.train.Saver()
    #saver.save(sess, './saved_model_fc8')

    pass
tests.test_train_nn(train_nn)


def run():
    num_classes = 2
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # Parameters
    epochs = 7
    batch_size = 4

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # Tensorflow variables or placeholders
        learning_rate = tf.placeholder(tf.float32)
        correct_label = tf.placeholder(tf.float32)

        # TODO: Build NN using load_vgg, layers, and optimize function
        input_image, keep_prob, layer3_out, layer4_out, layer7_out = load_vgg(sess, vgg_path)
        layer_output = layers(layer3_out, layer4_out, layer7_out, num_classes)
        logits, train_op, cross_entropy_loss = optimize(layer_output, correct_label, learning_rate, num_classes)
        # TODO: Train NN using the train_nn function
        print("Epochs:" +str(epochs))
        print("batch_size: " +str(batch_size))
        print("Keep_prob: "+str(keep_prob))
        print("Learning Rate: " +str(learning_rate))
        # Initialize all the Variables
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())

        train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image, correct_label, keep_prob, learning_rate)
        # TODO: Save inference data using helper.save_inference_samples
        #  helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)
        # OPTIONAL: Apply the trained model to a video


if __name__ == '__main__':
    run()
