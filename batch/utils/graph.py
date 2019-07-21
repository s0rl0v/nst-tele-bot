import numpy as np
import scipy.io
import scipy.misc
import tensorflow as tf

from utils.misc import *

def gram_matrix(A):
    """
    Argument:
    A -- matrix of shape (n_C, n_H*n_W)
    
    Returns:
    GA -- Gram matrix of A, of shape (n_C, n_C)
    """
    
    GA = tf.matmul(A, tf.transpose(A))
    
    return GA


class TFGraph:
    STYLE_LAYERS = [
        ('conv1_1', 0.2),
        ('conv2_1', 0.2),
        ('conv3_1', 0.2),
        ('conv4_1', 0.2),
        ('conv5_1', 0.2)
    ]

    def __init__(self, content_image, style_image, model_file, alpha = 10, beta = 40):
        self.alpha = alpha
        self.beta = beta
        tf.reset_default_graph()
        self.session = tf.InteractiveSession()

        self.content_image = scipy.misc.imread(content_image)
        self.content_image = reshape_and_normalize_image(self.content_image)

        self.style_image = scipy.misc.imread(style_image)
        self.style_image = reshape_and_normalize_image(self.style_image)

        self.generated_image = generate_noise_image(self.content_image)
        self.model = load_vgg_model(model_file)

        # Assign the content image to be the input of the VGG model.  
        self.session.run(self.model['input'].assign(self.content_image))

        # Select the output tensor of layer conv4_2
        out = self.model['conv4_2']

        # Set a_C to be the hidden layer activation from the layer we have selected
        a_C = self.session.run(out)

        # Set a_G to be the hidden layer activation from same layer. Here, a_G references model['conv4_2'] 
        # and isn't evaluated yet. Later in the code, we'll assign the image G as the model input, so that
        # when we run the session, this will be the activations drawn from the appropriate layer, with G as input.
        a_G = out

        # Compute the content cost
        self.J_content = self.__compute_content_cost(a_C, a_G)

        # Assign the input of the model to be the "style" image 
        self.session.run(self.model['input'].assign(self.style_image))

        # Compute the style cost
        self.J_style = self.__compute_style_cost()

        self.J = self.alpha * self.J_content + self.beta * self.J_style

        self.train_step = tf.train.AdamOptimizer(2.0).minimize(self.J)

    def __compute_content_cost(self, a_C, a_G):
        """
        Computes the content cost
        
        Arguments:
        a_C -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing content of the image C 
        a_G -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing content of the image G
        
        Returns: 
        J_content -- scalar that you compute using equation 1 above.
        """
        # Retrieve dimensions from a_G (≈1 line)
        m, n_H, n_W, n_C = a_G.get_shape().as_list()
        
        # Reshape a_C and a_G
        a_C_unrolled = tf.reshape(tf.transpose(a_C), [n_C, n_H * n_W])
        a_G_unrolled = tf.reshape(tf.transpose(a_G), [n_C, n_H * n_W])

        # compute the cost with tensorflow
        J_content = (1 / (4 * n_H * n_W * n_C)) * tf.reduce_sum(tf.square(tf.subtract(a_C_unrolled, a_G_unrolled)))
        
        return J_content

    def __compute_layer_style_cost(self, a_S, a_G):
        """
        Arguments:
        a_S -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing style of the image S 
        a_G -- tensor of dimension (1, n_H, n_W, n_C), hidden layer activations representing style of the image G
        
        Returns: 
        J_style_layer -- tensor representing a scalar value, style cost defined above by equation (2)
        """
        # Retrieve dimensions from a_G (≈1 line)
        m, n_H, n_W, n_C = a_G.get_shape().as_list()
        
        # Reshape the images to have them of shape (n_C, n_H*n_W) (≈2 lines)
        a_S = tf.transpose(tf.reshape(a_S,[n_H*n_W, n_C]))
        a_G = tf.transpose(tf.reshape(a_G,[n_H*n_W, n_C]))

        # Computing gram_matrices for both images S and G (≈2 lines)
        GS = gram_matrix(a_S)
        GG = gram_matrix(a_G)

        # Computing the loss (≈1 line)
        J_style_layer = tf.reduce_sum(tf.square(GS-GG))/(4*(n_C*n_W*n_H)**2)
        
        return J_style_layer
    
    def __compute_style_cost(self):
        """
        Computes the overall style cost from several chosen layers
        
        Arguments:
        model -- our tensorflow model
        STYLE_LAYERS -- A python list containing:
                            - the names of the layers we would like to extract style from
                            - a coefficient for each of them
        
        Returns: 
        J_style -- tensor representing a scalar value, style cost defined above by equation (2)
        """
        
        # initialize the overall style cost
        J_style = 0

        for layer_name, coeff in TFGraph.STYLE_LAYERS:

            # Select the output tensor of the currently selected layer
            out = self.model[layer_name]

            # Set a_S to be the hidden layer activation from the layer we have selected, by running the session on out
            a_S = self.session.run(out)

            # Set a_G to be the hidden layer activation from same layer. Here, a_G references model[layer_name] 
            # and isn't evaluated yet. Later in the code, we'll assign the image G as the model input, so that
            # when we run the session, this will be the activations drawn from the appropriate layer, with G as input.
            a_G = out

            # Compute style_cost for the current layer, Add coeff * J_style_layer of this layer to overall style cost
            J_style += coeff * (self.__compute_layer_style_cost(a_S, a_G))

        return J_style
    
    def run(self, num_iterations = 200):
        # Initialize global variables (you need to run the session on the initializer)
        self.session.run(tf.global_variables_initializer())
        
        # Run the noisy input image (initial generated image) through the model. Use assign().
        self.session.run(self.model['input'].assign(self.generated_image))
        
        for i in range(num_iterations):
        
            # Run the session on the train_step to minimize the total cost
            self.session.run(self.train_step)
            
            # Compute the generated image by running the session on the current model['input']
            ### START CODE HERE ### (1 line)
            generated_image = self.session.run(self.model['input'])
            ### END CODE HERE ###

            # Print every 20 iteration.
            if i % 10 == 0:
                Jt, Jc, Js = self.session.run([self.J, self.J_content, self.J_style])
                print("Iteration " + str(i) + " :")
                print("total cost = " + str(Jt))
                print("content cost = " + str(Jc))
                print("style cost = " + str(Js))
        return generated_image
