import tensorflow as tf
import os
import numpy as np
import cv2

NUM_CLASSES = 6 #分類するクラス数
IMG_SIZE = 28

#画像のあるディレクトリ
train_img_dirs = ['a', 'b', 'c', 'd', 'e', 'f']

#学習画像データ
train_image = []
#学習データのラベル
train_label = []

for i, d in enumerate(train_img_dirs):
     # ./data/以下の各ディレクトリ内のファイル名取得
    files = os.listdir('/Users/tadashintaro/desktop/zissou/data/' + d)

    for f in files:
        #画像読み込み
        img = cv2.imread('/Users/tadashintaro/desktop/zissou/data/' + d + '/' + f)
        try:
            #1辺がIMG_SIZEの正方形にリサイズ
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            #一列にして
            img = img.flatten().astype(np.float32)/255.0
            train_image.append(img)

            #one_hot_vectorを作りラベルとして追加
            tmp = np.zeros(NUM_CLASSES)
            tmp[i] = 1
            train_label.append(tmp)

        except Exception as e:
            #うまくいかないときは報告
            print(e)
            print("{}　ってうディレクトリの{}　っていうファイル確認".format(d,f))

#numpy配列に変換
train_image = np.asarray(train_image)
train_label = np.asarray(train_label)


sess = tf.InteractiveSession()
COLOR_CHANNELS = 3 # RGB
IMG_PIXELS = IMG_SIZE * IMG_SIZE * COLOR_CHANNELS # 画像のサイズ*RGB
x = tf.placeholder(tf.float32, shape=[None, IMG_PIXELS])
y_ = tf.placeholder(tf.float32, shape=[None, NUM_CLASSES])
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')
W_conv1 = weight_variable([5, 5, COLOR_CHANNELS, 32])
b_conv1 = bias_variable([32])
x_image = tf.reshape(x, [-1, IMG_SIZE, IMG_SIZE, COLOR_CHANNELS])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)
W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) +b_conv2)
h_pool2 = max_pool_2x2(h_conv2)
W_fc1 = weight_variable([7*7*64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) +b_fc1)
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
W_fc2 = weight_variable([1024, NUM_CLASSES])
b_fc2 = bias_variable([NUM_CLASSES])

y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) +b_fc2)

cross_entropy = tf.reduce_mean(
    tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))

train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))

accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess.run(tf.global_variables_initializer())

for i in range(20000):
    if i%100==0:
        train_accuracy = accuracy.eval(feed_dict={
            x:batch[0], y_: batch[1], keep_prob: 1.0})
        print("step %d, training accuracy %g"%(i, train_accuracy))
    train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
