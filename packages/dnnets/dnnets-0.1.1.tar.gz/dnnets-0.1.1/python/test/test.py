import os
import unittest
import dnnets

SAMPLE_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "sample_model.json")


class NoNumpy(unittest.TestCase):
    def setUp(self):
        dnnets.disable_numpy()

    def test_load(self):
        net = dnnets.load(SAMPLE_MODEL_PATH)
        input = [-3.5987e-01, -4.6701e-01, 1.6226e+00, 5.3634e-02]
        output = net.forward_pass(input)
        expected_out = [0.0178, -0.8575, 0.0877, 0.8729, -0.0683]
        self.assertEqual(len(expected_out), len(output))
        for i in range(len(output)):
            self.assertAlmostEqual(expected_out[i], output[i], places=4)

    def test_create(self):
        w1 = [[
            0.091522216796875,
            -0.3818141222000122,
            0.25633466243743896,
            0.7860110998153687
        ], [
            0.13578581809997559,
            0.2279491424560547,
            0.27909183502197266,
            0.02499675750732422
        ], [
            -0.40654075145721436,
            -0.44219744205474854,
            -0.4941016435623169,
            -0.7976804971694946
        ], [
            0.32486581802368164,
            0.7674628496170044,
            -0.16223323345184326,
            -0.13562500476837158
        ], [
            0.22599101066589355,
            0.9473749399185181,
            0.6816011667251587,
            -0.43894898891448975
        ], [
            0.06930303573608398,
            -0.8823517560958862,
            0.8848906755447388,
            -0.005420684814453125,
        ], [
            -0.5040081739425659,
            -0.9254074096679688,
            -0.3743274211883545,
            -0.16969871520996094,
        ], [
            -0.3569737672805786,
            0.03921496868133545,
            0.543988823890686,
            0.9798842668533325,
        ]]
        b1 = [
            -0.7117006778717041,
            -0.0065985918045043945,
            -0.2006610631942749,
            -0.5630269050598145,
            0.7903872728347778,
            -0.18012070655822754,
            -0.5960118770599365,
            0.6685824394226074,
        ]
        w2 = [[
            0.6051120758056641,
            0.7142164707183838,
            0.5969510078430176,
            0.6789673566818237,
            0.698874831199646,
            -0.7351524829864502,
            0.7911190986633301,
            -0.4360615015029907
        ], [
            -0.44526708126068115,
            -0.0931020975112915,
            -0.1796330213546753,
            0.9887782335281372,
            0.37523698806762695,
            -0.2600400447845459,
            0.5667493343353271,
            0.43812835216522217
        ], [
            -0.47426867485046387,
            -0.6671320199966431,
            0.6583425998687744,
            0.9937677383422852,
            -0.7600722312927246,
            -0.9207866191864014,
            -0.006901144981384277,
            -0.26735758781433105
        ], [
            -0.2612212896347046,
            0.10161864757537842,
            0.16390562057495117,
            -0.9009935855865479,
            0.10639607906341553,
            -0.02390313148498535,
            -0.343265175819397,
            -0.5574640035629272
        ], [
            0.5390497446060181,
            -0.4369018077850342,
            -0.8246228694915771,
            -0.3165513277053833,
            0.032694101333618164,
            -0.8689746856689453,
            -0.35116755962371826,
            0.780742883682251
        ], [
            0.4763883352279663,
            0.5816015005111694,
            -0.05206775665283203,
            -0.2541252374649048,
            0.6143609285354614,
            -0.16823148727416992,
            -0.6658449172973633,
            0.15097343921661377
        ]]
        b2 = [
            -0.6137567758560181,
            -0.7359094619750977,
            -0.4622260332107544,
            -0.5243713855743408,
            0.14157402515411377,
            -0.031595826148986816,
        ]
        w3 = [[
            0.022572755813598633,
            0.8377792835235596,
            -0.3033379316329956,
            -0.3415933847427368,
            -0.5881903171539307,
            0.9360156059265137
        ], [
            0.12421870231628418,
            0.3484431505203247,
            -0.11632287502288818,
            -0.41299355030059814,
            0.9819611310958862,
            -0.9323079586029053
        ], [
            0.6669166088104248,
            0.6997554302215576,
            0.15115857124328613,
            0.7219744920730591,
            -0.9155864715576172,
            0.1836148500442505
        ], [
            -0.7067359685897827,
            -0.18941938877105713,
            -0.38337409496307373,
            -0.2826213836669922,
            0.37848854064941406,
            -0.7259594202041626
        ], [
            -0.8018372058868408,
            -0.17787516117095947,
            -0.5953868627548218,
            0.280309796333313,
            0.6884880065917969,
            -0.5581295490264893
        ]]
        b3 = [
            0.7220213413238525,
            -0.8753236532211304,
            -0.4925537109375,
            0.6823080778121948,
            -0.4173605442047119,
        ]
        w4 = [
            0.11948883533477783,
            0.9049232006072998,
            0.3338879346847534,
            0.07458102703094482,
            0.6146050691604614,
        ]
        b4 = [
            -0.19932925701141357,
            0.004074811935424805,
            0.30791449546813965,
            0.8500757217407227,
            0.24645447731018066,
        ]

        mdef = dnnets.ModelDefinition(4)
        mdef.add_linear(8, w1, b1)
        mdef.add_elu(8)
        mdef.add_linear(6, w2, b2)
        mdef.add_relu(6)
        mdef.add_linear(5, w3, b3)
        mdef.add_tanh(5)
        mdef.add_layer_norm(5, w4, b4, eps=0.000001)
        mdef.add_clip(5, -2, 2)
        net = mdef.create()

        input = [-3.5987e-01, -4.6701e-01, 1.6226e+00, 5.3634e-02]
        output = net.forward_pass(input)
        expected_out = [0.0178, -0.8575, 0.0877, 0.8729, -0.0683]
        for i in range(len(output)):
            self.assertAlmostEqual(expected_out[i], output[i], places=4)


class WithNumpy(unittest.TestCase):
    def setUp(self):
        dnnets.enable_numpy()

    def test_load(self):
        import numpy as np

        net = dnnets.load(SAMPLE_MODEL_PATH)
        input = np.asarray(
            [-3.5987e-01, -4.6701e-01, 1.6226e+00, 5.3634e-02],
            dtype=np.float32)
        output = net.forward_pass(input)
        output_ref = net.out_buffer_ref()
        expected_out = np.asarray(
            [0.0178, -0.8575, 0.0877, 0.8729, -0.0683], dtype=np.float32)
        self.assertEqual(len(expected_out), len(output))
        for i in range(len(output)):
            self.assertAlmostEqual(expected_out[i], output[i], places=4)
            self.assertAlmostEqual(expected_out[i], output_ref[i], places=4)

    def test_against_pytorch(self):
        try:
            import torch
            import torch.nn as nn
            import torch.nn.functional as F
        except ImportError:
            return

        class SampleNetwork(nn.Module):
            def __init__(self):
                super(SampleNetwork, self).__init__()
                self.layer_norm = nn.LayerNorm(512)
                self.l1 = nn.Linear(512, 8192)
                self.l2 = nn.Linear(8192, 8192)
                self.l3 = nn.Linear(8192, 8192)
                self.l4 = nn.Linear(8192, 8192)
                self.l5 = nn.Linear(8192, 8192)
                self.l6 = nn.Linear(8192, 8192)
                self.l7 = nn.Linear(8192, 8192)
                self.l8 = nn.Linear(8192, 8192)
                self.l9 = nn.Linear(8192, 512)

                nn.init.normal_(self.layer_norm.weight)
                nn.init.normal_(self.l1.weight, std=0.01)
                nn.init.normal_(self.l2.weight, std=0.01)
                nn.init.normal_(self.l3.weight, std=0.01)
                nn.init.normal_(self.l4.weight, std=0.01)
                nn.init.normal_(self.l5.weight, std=0.01)
                nn.init.normal_(self.l6.weight, std=0.01)
                nn.init.normal_(self.l7.weight, std=0.01)
                nn.init.normal_(self.l8.weight, std=0.01)
                nn.init.normal_(self.l9.weight, std=0.01)
                nn.init.normal_(self.layer_norm.bias)
                nn.init.normal_(self.l1.bias, std=0.01)
                nn.init.normal_(self.l2.bias, std=0.01)
                nn.init.normal_(self.l3.bias, std=0.01)
                nn.init.normal_(self.l4.bias, std=0.01)
                nn.init.normal_(self.l5.bias, std=0.01)
                nn.init.normal_(self.l6.bias, std=0.01)
                nn.init.normal_(self.l7.bias, std=0.01)
                nn.init.normal_(self.l8.bias, std=0.01)
                nn.init.normal_(self.l9.bias, std=0.01)

            def forward(self, x):
                x = self.layer_norm(x)
                x = F.elu(self.l1(x))
                x = F.elu(self.l2(x))
                x = F.elu(self.l3(x))
                x = F.elu(self.l4(x))
                x = F.elu(self.l5(x))
                x = F.elu(self.l6(x))
                x = F.elu(self.l7(x))
                x = F.elu(self.l8(x))
                x = F.elu(self.l9(x))
                return x

        device = torch.device("cpu")
        torch_model = SampleNetwork().to(device)

        def tensor_to_list(tensor):
            return tensor.detach().cpu().numpy()

        mdef = dnnets.ModelDefinition(512)
        for module in torch_model.modules():
            if isinstance(module, nn.Linear):
                weight = tensor_to_list(module.weight)
                bias = tensor_to_list(module.bias)
                mdef.add_linear(len(bias), weight, bias)
                mdef.add_elu(len(bias))
            elif isinstance(module, nn.LayerNorm):
                weight = tensor_to_list(module.weight)
                bias = tensor_to_list(module.bias)
                mdef.add_layer_norm(len(bias), weight, bias, eps=module.eps)

        dnnets_model = mdef.create()

        dummy_input = torch.randn(512)
        with torch.no_grad():
            torch_out = torch_model(dummy_input)
        dummy_input_numpy = dummy_input.numpy()
        dnnets_model.forward_pass_no_out(dummy_input_numpy)
        dnnets_out = dnnets_model.out_buffer_ref()
        torch_out = torch_out.numpy()
        self.assertEqual(len(torch_out), len(dnnets_out))
        for i in range(len(torch_out)):
            self.assertAlmostEqual(torch_out[i], dnnets_out[i], places=2)
