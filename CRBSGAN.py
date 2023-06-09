#CRBSGAN for MNIST DATA
import utils, torch, time, os, pickle
import matplotlib.pyplot as plt

import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from dataloader import dataloader
import torchvision.transforms as transforms
import torchvision
transform = transforms.Compose([transforms.RandomHorizontalFlip(), 
                                transforms.RandomAffine(0, (1/8,0))]) 

def nll_loss_neg(y_pred, y_true):
    out = torch.sum(y_true * y_pred, dim=1)
    return torch.mean(- torch.log((1 - out) + 1e-6))

def nll_loss_neg2(y_pred, y_true):
    out = torch.sum(y_true * y_pred, dim=1)
    return torch.mean(- torch.log(( out) + 1e-6))


l2loss = nn.MSELoss()



class generator(nn.Module):

    def __init__(self, input_dim=100, output_dim=1, input_size=32):
        super(generator, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.input_size = input_size

        self.fc = nn.Sequential(
            nn.Linear(self.input_dim, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Linear(1024, 128 * (self.input_size // 4) * (self.input_size // 4)),
            nn.BatchNorm1d(128 * (self.input_size // 4) * (self.input_size // 4)),
            nn.ReLU(),
        )
        self.deconv = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.ConvTranspose2d(64, self.output_dim, 4, 2, 1),
            nn.Tanh(),
        )
        utils.initialize_weights(self)

    def forward(self, input):
        x = self.fc(input)
        x = x.view(-1, 128, (self.input_size // 4), (self.input_size // 4))
        x = self.deconv(x)

        return x



class discriminator(nn.Module):

    def __init__(self, input_dim=1, output_dim=1, input_size=32):
        super(discriminator, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.input_size = input_size

        self.conv = nn.Sequential(
            nn.Conv2d(self.input_dim, 64, 4, 2, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
        )
        self.fc = nn.Sequential(
            nn.Linear(128 * (self.input_size // 4) * (self.input_size // 4), 1024),
            nn.BatchNorm1d(1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, self.output_dim),
            nn.Sigmoid(),
        )
        utils.initialize_weights(self)

    def forward(self, input):
        x = self.conv(input)
        x = x.view(-1, 128 * (self.input_size // 4) * (self.input_size // 4))
        x = self.fc(x)

        return x



class classifier(nn.Module):
    def __init__(self):
        super(classifier, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 10)
        utils.initialize_weights(self)

        self.softmax = nn.Softmax()

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return self.softmax(x), F.log_softmax(x, dim=1)


class CRBSGAN(object):
    def __init__(self, args):

        self.epoch = args.epoch
        self.sample_num = 100
        self.batch_size = args.batch_size
        self.save_dir = args.save_dir
        self.result_dir = args.result_dir
        self.dataset = args.dataset
        self.log_dir = args.log_dir
        self.gpu_mode = True
        self.model_name = args.gan_type
        self.input_size = args.input_size
        self.z_dim = 62
        self.num_labels = args.num_labels
        self.index = args.index
        self.lrC = args.lrC

        self.labeled_loader, self.unlabeled_loader, self.test_loader = dataloader(self.dataset, self.input_size, self.batch_size, self.num_labels)
        data = self.labeled_loader.__iter__().__next__()[0]

        self.G = generator(input_dim=self.z_dim, output_dim=data.shape[1], input_size=self.input_size)
        self.D = discriminator(input_dim=data.shape[1], output_dim=1, input_size=self.input_size)
        self.C = classifier()
        self.G_optimizer = optim.Adam(self.G.parameters(), lr=args.lrG, betas=(args.beta1, args.beta2))
        self.D_optimizer = optim.Adam(self.D.parameters(), lr=args.lrD, betas=(args.beta1, args.beta2))
        self.C_optimizer = optim.SGD(self.C.parameters(), lr=args.lrC, momentum=args.momentum)

        if self.gpu_mode:
            self.G.cuda()
            self.D.cuda()
            self.C.cuda()
            self.BCE_loss = nn.BCELoss().cuda()
        else:
            self.BCE_loss = nn.BCELoss()

        print('---------- Networks architecture -------------')
        utils.print_network(self.G)
        utils.print_network(self.D)
        utils.print_network(self.C)
        print('-----------------------------------------------')


        self.sample_z_ = torch.rand((self.batch_size, self.z_dim))
        if self.gpu_mode:
            self.sample_z_ = self.sample_z_.cuda()

    def train(self):
        self.train_hist = {}
        self.train_hist['D_loss'] = []
        self.train_hist['G_loss'] = []
        self.train_hist['C_loss'] = []
        self.train_hist['per_epoch_time'] = []
        self.train_hist['total_time'] = []
        self.train_hist['C_real_loss']=[]
        self.train_hist['test_loss']=[]
        self.train_hist['correct_rate']=[]
        self.train_hist['exit']=[]
        self.best_acc = 0
        self.best_time = 0

        self.y_real_, self.y_fake_ = torch.ones(self.batch_size, 1), torch.zeros(self.batch_size, 1)
        if self.gpu_mode:
            self.y_real_, self.y_fake_ = self.y_real_.cuda(), self.y_fake_.cuda()

        self.D.train()
        print('training start!!')
        start_time = time.time()
        for epoch in range(self.epoch):
            cla=0
            dloss=0
            gloss=0
            self.G.train()
            epoch_start_time = time.time()

            if epoch == 0:
                correct_rate = 0
                while True:
                    cr=0
                    for iter, (x_, y_) in enumerate(self.labeled_loader):
                        if self.gpu_mode:
                            x_, y_ = x_.cuda(), y_.cuda()
                        self.C.train()
                        self.C_optimizer.zero_grad()
                        _, C_real = self.C(x_)
                        C_real_loss = F.nll_loss(C_real, y_)
                        C_real_loss.backward()
                        self.C_optimizer.step()
                        cr+=C_real_loss.item()


                        if iter == self.labeled_loader.dataset.__len__() // self.batch_size:
                            self.C.eval()
                            test_loss = 0
                            correct = 0
                            with torch.no_grad():
                                for data, target in self.test_loader:
                                    data, target = data.cuda(), target.cuda()
                                    _, output = self.C(data)
                                    test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
                                    pred = output.argmax(dim=1, keepdim=True) # get the index of the max log-probability
                                    correct += pred.eq(target.view_as(pred)).sum().item()
                            test_loss /= len(self.test_loader.dataset)

                            print('\niter: {} Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
                                (iter), test_loss, correct, len(self.test_loader.dataset),
                                100. * correct / len(self.test_loader.dataset)
                                ))
                            correct_rate = correct / len(self.test_loader.dataset)
                            
                    cr /=self.labeled_loader.dataset.__len__()
                    self.train_hist['test_loss'].append(test_loss)
                    self.train_hist['C_real_loss'].append(cr)
                    self.train_hist['correct_rate'].append(correct_rate)
                    
                    gate = 0.8
                    if self.num_labels == 600:
                        gate = 0.93
                    elif self.num_labels == 1000:
                        gate = 0.95
                    elif self.num_labels == 3000:
                        gate = 0.97
                    if correct_rate > gate:
                        self.train_hist['exit'].append(len(self.train_hist['correct_rate']))
                        break

            correct_wei = 0
            number = 0
            labeled_iter = self.labeled_loader.__iter__()
            for iter, (x_u, y_u) in enumerate(self.unlabeled_loader):
                self.C.train()
                if iter == self.unlabeled_loader.dataset.__len__() // self.batch_size:
                    if epoch > 0:
                        print('\nPseudo tag: Accuracy: {}/{} ({:.0f}%)\n'.format(
                            correct_wei, number,
                            100. * correct_wei / number))
                    break

                try:
                    x_l, y_l = labeled_iter.__next__()
                except StopIteration:
                    labeled_iter = self.labeled_loader.__iter__()
                    x_l, y_l = labeled_iter.__next__()

                z_ = torch.rand((self.batch_size, self.z_dim))
                if self.gpu_mode:
                    x_l, y_l, x_u, y_u, z_ = \
                        x_l.cuda(), y_l.cuda(), x_u.cuda(), y_u.cuda(), z_.cuda()


                self.C_optimizer.zero_grad()

                _, C_labeled_pred = self.C(x_l)
                C_labeled_loss = F.nll_loss(C_labeled_pred, y_l)

                T_x = transform(x_l)
                C_labeledtprob,C_labeledt = self.C(T_x)
                #pseudo-labeling+ consistency
                C_label_wei = y_l
                C_label_wei = C_label_wei.view(-1, 1)
                mostLikelyProbs = np.asarray([C_labeledtprob[i, C_label_wei[i]].item() for  i in range(len(C_labeledtprob))])
                confidenceThresh = 0.98
                toKeep = mostLikelyProbs > confidenceThresh
                if sum(toKeep) != 0:
                    print(sum(toKeep))
                    C_label_wei1 = torch.zeros(sum(toKeep), 10).cuda().scatter_(1, C_label_wei[toKeep], 1)
                    C_label_wei2 = torch.zeros(sum(~toKeep), 10).cuda().scatter_(1, C_label_wei[~toKeep], 1)
                    L_reall1Ch = nll_loss_neg2(C_label_wei1, C_labeledtprob[toKeep])
                    L_reall1Ch.backward()


                C_unlabeled_pred1, C_unlabeled_pred = self.C(x_u)
                C_unlabeled_wei = torch.max(C_unlabeled_pred, 1)[1]

                correct_wei += C_unlabeled_wei.eq(y_u).sum().item()
                number += len(y_u)
                C_unlabeled_loss = F.nll_loss(C_unlabeled_pred,  C_unlabeled_wei)
               


                T_x = transform(x_u)

                C_unlabeled_predt, _ = self.C(T_x)


               


                G_ = self.G(z_)
                C_fake_pred, _ = self.C(G_)
                C_fake_wei = torch.max(C_fake_pred, 1)[1]
                C_fake_wei = C_fake_wei.view(-1, 1)
                C_fake_wei = torch.zeros(self.batch_size, 10).cuda().scatter_(1, C_fake_wei, 1)
                C_fake_loss = nll_loss_neg(C_fake_wei, C_fake_pred)




                C_loss = C_labeled_loss + C_unlabeled_loss + C_fake_loss
                self.train_hist['C_loss'].append(C_loss.item())

                C_loss.backward()
                self.C_optimizer.step()


                self.D_optimizer.zero_grad()

                D_labeled = self.D(x_l)
                D_labeled_loss = self.BCE_loss(D_labeled, torch.ones_like(D_labeled))


                D_unlabeled = self.D(x_u)
                D_unlabeled_loss = self.BCE_loss(D_unlabeled, torch.ones_like(D_unlabeled))

                G_ = self.G(z_)
                D_fake = self.D(G_.detach())
                D_fake_loss = self.BCE_loss(D_fake, self.y_fake_)

                T_x = transform(G_.detach())
                D_faket = self.D(T_x)
                L_D_fake1 = l2loss(D_fake , D_faket )
                
                
                #Discriminator+ consistency

                T_x = transform(x_l)
                D_labeledt = self.D(T_x)
                L_reall1 = l2loss(D_labeled , D_labeledt )

                T_x = transform(x_u)
                D_unlabeledt = self.D(T_x)
                L_realu2 = l2loss(D_unlabeled , D_unlabeledt )

                D_fake_loss = self.BCE_loss(D_fake, self.y_fake_)

                T_z = z_ + torch.normal(0,1,z_.shape).cuda()
                G_T_z = self.G(T_z)
                D_G_T_z = self.D(G_T_z.detach())
                L_dis = l2loss(D_fake, D_G_T_z)
                D_loss = D_labeled_loss + D_unlabeled_loss + D_fake_loss+((L_reall1+L_realu2+L_D_fake1)*10)+L_dis*5

                D_loss.backward()
                self.D_optimizer.step()


                self.G_optimizer.zero_grad()

                G_ = self.G(z_)
                T_z = z_ + torch.normal(0,1,z_.shape).cuda()
                G_T_z = self.G(T_z)


                D_fake = self.D(G_)
                G_loss_D = self.BCE_loss(D_fake, self.y_real_)


                #Generator+ consistency

                L_gen = -l2loss(G_, G_T_z)

                _, C_fake_pred = self.C(G_)
                C_fake_wei = torch.max(C_fake_pred, 1)[1]
                G_loss_C  = F.nll_loss(C_fake_pred, C_fake_wei)

                G_loss = G_loss_D + G_loss_C+L_gen*0.5


                G_loss.backward()
                self.G_optimizer.step()

                if ((iter + 1) % 100) == 0:
                    print("Epoch: [%2d] [%4d/%4d] D_loss: %.8f, G_loss: %.8f, C_loss: %.8f" %
                          (
                          (epoch + 1), (iter + 1), self.unlabeled_loader.dataset.__len__() // self.batch_size, D_loss.item(),
                          G_loss.item(), C_loss.item()))
                cla+=C_loss.item()
                dloss+=D_loss.item()
                gloss+=G_loss.item()
                

            self.C.eval()
            test_loss = 0
            correct = 0
            with torch.no_grad():
                for data, target in self.test_loader:
                    data, target = data.cuda(), target.cuda()
                    _, output = self.C(data)
                    test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
                    pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
                    correct += pred.eq(target.view_as(pred)).sum().item()

            test_loss /= len(self.test_loader.dataset)

            acc = 100. * correct / len(self.test_loader.dataset)
            cur_time = time.time() - start_time
            with open('acc_time/LUG/' + str(self.num_labels) + '_' + str(self.index) + '_' + str(self.lrC) + '.txt', 'a') as f:
                f.write(str(cur_time) + ' ' + str(acc) + '\n')

            cla/=self.unlabeled_loader.dataset.__len__()
            dloss/=self.unlabeled_loader.dataset.__len__()
            gloss/=self.unlabeled_loader.dataset.__len__()
            self.train_hist['D_loss'].append(dloss)
            self.train_hist['G_loss'].append(gloss)
            self.train_hist['test_loss'].append(test_loss)
            self.train_hist['C_real_loss'].append(cla)
            self.train_hist['correct_rate'].append(acc)
            if acc > self.best_acc:
                self.best_acc = acc
                self.best_time = cur_time

            print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
                test_loss, correct, len(self.test_loader.dataset),
                100. * correct / len(self.test_loader.dataset)))

            self.train_hist['per_epoch_time'].append(time.time() - epoch_start_time)
            with torch.no_grad():
                self.visualize_results((epoch + 1))

        with open('acc_time/LUG/' + str(self.num_labels) + '_' + str(self.lrC) + '_best.txt', 'a') as f:
            f.write(str(self.index) + ' ' + str(self.best_time) + ' ' + str(self.best_acc) + '\n')
        self.train_hist['total_time'].append(time.time() - start_time)
        print("Avg one epoch time: %.2f, total %d epochs time: %.2f" % (np.mean(self.train_hist['per_epoch_time']),
                                                                        self.epoch,
                                                                        self.train_hist['total_time'][0]))
        print("Training finish!... save training results")

        self.save()


    def visualize_results(self, epoch, fix=True):
        self.G.eval()

        path = self.result_dir + '/LUG/' + self.model_name + '_' + str(self.index)

        if not os.path.exists(path):
            os.makedirs(path)

        tot_num_samples = min(self.sample_num, self.batch_size)
        image_frame_dim = int(np.floor(np.sqrt(tot_num_samples)))

        if fix:
            """ fixed noise """
            samples = self.G(self.sample_z_)
        else:
            """ random noise """
            sample_z_ = torch.rand((self.batch_size, self.z_dim))
            if self.gpu_mode:
                sample_z_ = sample_z_.cuda()

            samples = self.G(sample_z_)

            
        samples1=samples


        if self.gpu_mode:
            samples = samples.cpu().data.numpy().transpose(0, 2, 3, 1)
        else:
            samples = samples.data.numpy().transpose(0, 2, 3, 1)

        samples = (samples + 1) / 2
        utils.save_images(samples[:image_frame_dim * image_frame_dim, :, :, :], [image_frame_dim, image_frame_dim],
                          path + '/' + self.model_name + '_epoch%03d' % epoch + '.png')
        gridOfFakeImages = torchvision.utils.make_grid((samples1 + 1) / 2)
        torchvision.utils.save_image(gridOfFakeImages,path + '/' + self.model_name + '_epoch%03d' % epoch + '.pdf')

    def save(self):

        save_dir = self.save_dir + '/LUG/' + self.model_name + '_' + str(self.index)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        torch.save(self.G.state_dict(), os.path.join(save_dir, self.model_name + '_G.pkl'))
        torch.save(self.D.state_dict(), os.path.join(save_dir, self.model_name + '_D.pkl'))

        with open(os.path.join(save_dir, self.model_name + '_history.pkl'), 'wb') as f:
            pickle.dump(self.train_hist, f)

    def load(self):
        save_dir = os.path.join(self.save_dir, self.dataset, self.model_name)

        self.G.load_state_dict(torch.load(os.path.join(save_dir, self.model_name + '_G.pkl')))
        self.D.load_state_dict(torch.load(os.path.join(save_dir, self.model_name + '_D.pkl')))
