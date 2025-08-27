import itertools

import numpy as np
from ase.calculators.vasp import VaspChargeDensity
from ase.dft.stm import dos2current
from ase.geometry import wrap_positions
from surface_construct.structures.surface_grid import SurfaceGrid
from scipy.interpolate import interpn, griddata


class STM:
    """
    Simulate STM image from VASP PARCHG.
    """

    def __init__(self, bias=None):
        self.sg_obj = None
        self.current = None
        self.atoms = None
        self.density = None
        self.ngridpoints = np.array([0, 0, 0])
        if bias is None or bias == 0:
            "TODO: Read from INCAR EINT"
            self.bias = 0.1
            self.bias_range = (0, 0.1)
        elif type(bias) in (list, tuple):
            self.bias = np.abs(bias).max()
            self.bias_range = bias
        elif type(bias) in (float, int):
            self.bias = bias
            self.bias_range = sorted((0, bias))
        self.height = None
        self.scan_mode = None
        self.x, self.y, self.data = None, None, None
        self.kwargs = {
            'current': None,
            'bottom': False,
            'repeat': (1,1),
            'startpoint': None,
            'plot': True,
        }

    def read_parchg(self, filename='PARCHG'):
        print("Reading PARCHG file now...\n")
        vasp_charge = VaspChargeDensity(filename)
        self.density = vasp_charge.chg[-1]
        self.atoms = vasp_charge.atoms[-1]
        self.ngridpoints = np.array(self.density.shape)
        # Read scaling factor and unit cell of the crystal structure.
        self._cellz = self.atoms.cell.lengths()[2]
        self._zinterval = self._cellz / self.ngridpoints[2]

        del vasp_charge
        print("Done!\n")

    def get_avg_current_from_height(self, height, bottom=False):
        if bottom:
            height = self.atoms.positions[:, 2].min() - height
        else:
            height = self.atoms.positions[:, 2].max() + height

        self.scan_mode = 'constant_current'
        self.height = height

        n2 = height / self._cellz * self.ngridpoints[2]  # this means scanning must be in c direction
        dn2 = n2 - np.floor(n2)
        n2 = int(n2) % self.ngridpoints[2]
        # Get the averaged current. 这里使用的是 最大/最小值的平均值，而不是总的平均值.
        # I don't understand this part. It is not an average but max-min
        # averaged_current = ((1 - dn2) * self.density[:, :, n2].ptp()
        #                    + dn2 * self.density[:, :, (n2 + 1) % self.ngridpoints[2]].ptp())
        averaged_current = ((1 - dn2) * np.average(self.density[:, :, n2])
                            + dn2 * np.average(self.density[:, :, (n2 + 1) % self.ngridpoints[2]]))

        averaged_current = dos2current(self.bias, averaged_current)
        return averaged_current

    def get_avg_current(self, height=None, bottom=False):
        if bottom:
            print("Since SurfaceGrid doesn't support bottom yet, use get_avg_current_from_height.")
            return self.get_avg_current_from_height(height, bottom)
        rads = 0.76 + (height or 0)  # the radius of tip, default is radius of C
        self.height = self.atoms.positions[:, 2].max() + rads
        sg_obj = SurfaceGrid(self.atoms, interval=0.1, rads=rads, lpca=False)
        sg_obj.gridize(subtype='slab')
        self.sg_obj = sg_obj
        print(f"Generated {len(sg_obj.points)} grid points")
        f_grid_points = self.atoms.cell.scaled_positions(self.sg_obj.points)
        currents = dos2current(self.bias, self.density)
        xyz = [np.linspace(0, 1, n) for n in currents.shape]
        interp_values = interpn(xyz, currents, f_grid_points,
                                method='linear', bounds_error=False, fill_value=None)
        mean_current = interp_values.mean()
        return mean_current


    def _tile_data(self, values, repeat):
        s0 = values.shape = self.density.shape[:2]
        values = np.tile(values, repeat)
        s = values.shape

        ij = np.indices(s, dtype=float).reshape((2, -1)).T
        x, y = np.dot(ij / s0, self.atoms.cell[:2, :2]).T.reshape((2,) + s)

        self.x = x
        self.y = y
        self.data = values

    def _scan_current(self, **kwargs):
        if kwargs['current'] is None:
            height = kwargs['height'] or 0.0
            current = self.get_avg_current(height, kwargs['bottom'])
        else:
            current = kwargs['current']

        self.current = current
        density = self.density.reshape((-1, self.ngridpoints[2]))
        density = dos2current(self.bias, density)
        heights = self._find_heights(density, current)

        self._tile_data(heights, kwargs['repeat'])


    def _find_heights(self, currents, current):
        assert current > 0
        heights = np.empty(currents.shape[0])
        self.current = current
        startpoint = self.kwargs.get('startpoint')
        for i, den in enumerate(currents):
            if self.kwargs['bottom']:
                n = 1
                if startpoint is not None:
                    n = int(startpoint * self.ngridpoints[2])
                while n < self.ngridpoints[2]:
                    if den[n] > current:
                        break
                    n += 1
                else:
                    n = 1
                c1, c2 = den[n-1:n+1]
                heights[i] = (n - (c2 - current) / (c2 - c1)) * self._zinterval
            else:
                n = self.ngridpoints[2] - 1
                if startpoint is not None:
                    n = int(startpoint * self.ngridpoints[2]) - 1
                else:
                    while den[n].max() > current * 0.1:
                        n -= 1
                while n > 0:
                    if den[n] > current:
                        break
                    n -= 1
                else:
                    n = self.ngridpoints[2] - 1
                c2, c1 = den[n:n+2]
                heights[i] = (n + (c2 - current) / (c2 - c1)) * self._zinterval
            if not c1 <= current <= c2:
                if i != 0:
                    heights[i] = heights[i-1]
                else:
                    raise ValueError("Density values error!")
        return heights

    def _scan_height(self, **kwargs):
        height = kwargs['height'] or 2.0
        if kwargs['bottom']:
            height = self.atoms.positions[:, 2].min() - height
        else:
            height = self.atoms.positions[:, 2].max() + height
        self.height = height
        nz = self.ngridpoints[2]
        ldos = self.density.reshape((-1, nz))

        I = np.empty(ldos.shape[0])

        zp = height / self.atoms.cell[2, 2] * nz
        dz = zp - np.floor(zp)
        zp = int(zp) % nz

        for i, a in enumerate(ldos):
            I[i] = dos2current(self.bias, (1 - dz) * a[zp] + dz * a[(zp + 1) % nz])

        self._tile_data(I, kwargs['repeat'])

    def dI_dz(self):
        if self.kwargs['bottom']:
            f = -1
        else:
            f = 1
        if self.scan_mode == 'constant_height':
            self.kwargs['height'] += self._zinterval * 2
            data0 = self.data.copy()
            self._scan_height(**self.kwargs)
            dI = (self.data - data0)
            dz = self._zinterval * 2
        elif self.scan_mode == 'constant_current':
            current = self.current
            current_plus = current / 1.5
            height0 = self.data.copy()
            self.kwargs['current'] = current_plus
            self._scan_current(**self.kwargs)
            dI = current_plus - current
            dz = self.data - height0
        else:
            raise NotImplementedError
        result = dI / dz * f
        if self.kwargs['plot']:
            self.plot(self.x, self.y, result, reverse=self.kwargs['bottom'], absolute=True, label='dI-dz_')
        return result

    def scan(self, scan_mode='constant_current', height=None, **kwargs):
        """
        :param scan_mode: choices are 'constant_height', 'constant_current'
        :param height: float. The distance from tip to the highest atom of surface.
            For constant_height mode, it is the setting value.
            For constant_current mode, it is for obtain the average current at this height.
        :param current: float. The setting value for 'constant_current' mode.
        :param bottom: bool. Whether the surface is the bottom of slab.
        :param repeat: tuple or list. Output figure repeat in x,y direction.
        :param plot: bool. Whether plot or not output.
        :param startpoint: float. The starting point of the scan,
            which can save some time to find the height. Only for constant_current mode.
        :return: np.array. The grid data of height or current.
        """

        self.kwargs.update(kwargs)
        self.kwargs['height'] = height
        scan_mode_options = ['constant_height', 'constant_current']
        if scan_mode == 'constant_current':
            scan_func = self._scan_current
            self.scan_mode = scan_mode
        elif scan_mode == 'constant_height':
            scan_func = self._scan_height
            self.scan_mode = scan_mode
        else:
            raise ValueError("Scan mode options: ", scan_mode_options)
        scan_func(**self.kwargs)
        if self.kwargs['plot']:
            self.plot(self.x, self.y, self.data, reverse=self.kwargs['bottom'], absolute=False)

        return self.x, self.y, self.data

    def plot(self, x=None, y=None, data=None, reverse=False, absolute=False, label=''):
        """
        Suggest colormap: afmhot, gist_heat
        :param absolute:
        :param y:
        :param x:
        :param reverse:
        :param data:
        :return:
        """
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if data is None:
            data = self.data

        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        # import matplotlib.cm as cm
        scan_mode = self.scan_mode

        plt.figure()
        plt.rcParams['figure.max_open_warning'] = 50
        plt.gca().set_aspect('equal')
        plt.axis('off')
        plt.xticks(())
        plt.yticks(())
        cm = plt.cm.get_cmap('%s' % 'gist_heat')
        if not absolute:
            if scan_mode == 'constant_current':
                if reverse:
                    minh = data.max()  # reference point
                    data = minh - data
                else:
                    minh = data.min()
                    data = data - minh
        plt.contourf(x, y, data, 900, cmap=cm)
        plt.colorbar()
        if scan_mode == 'constant_height':
            mode_label = 'H'
        elif scan_mode == 'constant_current':
            mode_label = 'C'
        else:
            mode_label = 'None'
            print("Not support scan mode,", scan_mode)

        plt.savefig(f'{label}{mode_label}_{round(self.height or 0, 3)}.png',
                    dpi=300, bbox_inches='tight')

    def delta_h(self, repeat=(1,1), plot=True):
        """
        Calculate the delta height between sg_obj.points and stm height.
        :return: dh
        """
        if self.scan_mode == 'constant_height':
            print("Not support constant height mode.")
            return None
        if not getattr(self, 'sg_obj'):
            zmax = self.atoms.positions[:, 2].max()
            height = (self.height or zmax) - zmax  # bottom is False
            rads = 0.76 + height  # the radius of tip, default is radius of C
            sg_obj = SurfaceGrid(self.atoms, interval=0.1, rads=rads, lpca=False)
            sg_obj.gridize(subtype='slab')
            self.sg_obj = sg_obj
            print(f"Generated {len(sg_obj.points)} grid points")

        grid_points = self.sg_obj.points
        gx = grid_points[:, 0]
        gy = grid_points[:, 1]
        gz = grid_points[:, 2]
        xy_points = np.column_stack((gx, gy, np.zeros_like(gx)))
        xy_wrapped = wrap_positions(
            xy_points,
            self.atoms.cell,
            pbc=[True, True, False],  # 仅xy方向周期性
            center=(0.5, 0.5, 0.5),
            pretty_translation=True,
            eps=1e-07
        )
        wrapped_points = np.column_stack((xy_wrapped[:, 0], xy_wrapped[:, 1], gz))
        ranges = [np.arange(p) for p in repeat]
        hkls = np.concatenate([np.array(list(itertools.product(*ranges))),
                               np.zeros([np.prod(repeat), 1], dtype=int)], axis=1)
        vrvecs = hkls @ self.atoms.cell
        super_points = np.concatenate(wrapped_points + vrvecs[:,None], axis=0)

        if repeat != self.kwargs['repeat']:
            self.kwargs['repeat'] = repeat
            self._scan_current(**self.kwargs)

        interplo_z = griddata(
            super_points[:, :2],  # 包装后的xy坐标
            super_points[:, 2],  # 原始z高度
            (self.x, self.y),  # STM网格点
            method='nearest',
        )
        dh = self.data - interplo_z
        self.sg_obj.points = np.array([self.x.flatten(),
                                       self.y.flatten(),
                                       interplo_z.flatten()]).T
        if plot:
            self.plot(self.x, self.y, dh, absolute=True, label='dh_')
        return dh