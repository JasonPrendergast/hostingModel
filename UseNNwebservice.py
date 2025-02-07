import tensorflow as tf
import pickle
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from bottle import route, run, request

#Creating Globals 
lemmatizer = WordNetLemmatizer()

n_nodes_hl1 = 500
n_nodes_hl2 = 500

n_classes = 2
hm_data = 2000000

batch_size = 32
hm_epochs = 10
#tf.reset_default_graph()
x = tf.placeholder('float')
y = tf.placeholder('float')


current_epoch = tf.Variable(1)

hidden_1_layer = {'f_fum':n_nodes_hl1,
                  'weight':tf.Variable(tf.random_normal([2638, n_nodes_hl1])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl1]))}

hidden_2_layer = {'f_fum':n_nodes_hl2,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl2]))}

output_layer = {'f_fum':None,
                'weight':tf.Variable(tf.random_normal([n_nodes_hl2, n_classes])),
                'bias':tf.Variable(tf.random_normal([n_classes])),}

#Define the network shape
def neural_network_model(data):

    l1 = tf.add(tf.matmul(data,hidden_1_layer['weight']), hidden_1_layer['bias'])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weight']), hidden_2_layer['bias'])
    l2 = tf.nn.relu(l2)

    output = tf.matmul(l2,output_layer['weight']) + output_layer['bias']

    return output
#create the saver
saver = tf.train.import_meta_graph('./model.ckpt.meta')
#Use the network for training
def use_neural_network(input_data):
    prediction = neural_network_model(x)
    with open('lexicon-2500-2638.pickle','rb') as f:
        lexicon = pickle.load(f)
        
    with tf.Session() as sess:
        #tf.reset_default_graph()
        sess.run(tf.global_variables_initializer())
        #tf.reset_default_graph()
        saver.restore(sess,"model.ckpt")
        #print('model restored')
        current_words = word_tokenize(input_data.lower())
        current_words = [lemmatizer.lemmatize(i) for i in current_words]
        features = np.zeros(len(lexicon))

        for word in current_words:
            if word.lower() in lexicon:
                index_value = lexicon.index(word.lower())
                # OR DO +=1, test both
                features[index_value] += 1

        features = np.array(list(features))
        # pos: [1,0] , argmax: 0
        # neg: [0,1] , argmax: 1
        result = (sess.run(tf.argmax(prediction.eval(feed_dict={x:[features]}),1)))
        if result[0] == 0:
            print('Positive:',input_data)
            return 'Positive:',input_data
        elif result[0] == 1:
            #Print('Neg')
            print('Negative:',input_data)
            return 'Negative:',input_data
            
#use the network for predictions/classification
#http://127.0.0.1:12345/posneg?blog=I%20hate%20fish&key=test1
@route('/posneg')
def index():
    if request.GET.get('key') == 'test1':
		
        return str(use_neural_network(request.GET.get('blog')))
		#str(int(request.GET.get('number1')) + int(request.GET.get('number2')))
    else:
        return 'Unsupported operation'
#start the server hosting the network
if __name__ == '__main__':
	#run
    run(host='127.0.0.1', port=12345)

#use_neural_network("He's an idiot and a jerk.")
#use_neural_network("This was the best store i've ever seen.")
#use_neural_network("I really hate that boy he totally suck")
