# stm_sim
 
An STM simulation python library from LDOS.

## Installation

pip install -U stm-sim

**Requirements**
* ASE
* surface_construct
* Mayavi (optional)

## Usage

```python
from stm_sim.stm import STM
parchg_file = "PARCHG"
stm = STM(bias=(-0.1, 0.1))
stm.read_parchg(parchg_file)
x, y, z = stm.scan(scan_mode='constant_current', repeat=(2, 2), plot=True)
```

**Parameters**

* `scan_mode`: default is `constant_current`, support `constant_height` and `constant_current`
* `repeat`: repeat the simulated image along x,y axes
* `plot`: plot it with matplotlib or not, default is `False`
* `startpoint`:  set the start point to find height can save time, used for `scan_mode='constant_current'`.
* `height`: 
  * The height for `scan_mode='constant_height'`. 
  * For `scan_mode='constant_current'`, it is for the height of tip to obtain the average current: h_tip = height + 0.76, 0.76 is the radius of carbon.
    * For `bottom=True`, it use old `get_avg_current_from_height`.
* `bottom`: upper or bottom side of slab, default is `False`


## TODO
* Export 2d data for external program plot.
* Generate INCAR for vasp task
* Support other program, like cp2k, fireball, fhi-aims, integrate multiwfn
* Use api design
* Autofocus method: height auto choose, current auto choose, bias auto choose
  * 使用傅立叶变换，目标是主频频率需要满足特定的规则，需要扩包；黑白要分明，最好对半分；高度差要在一个范围里面，用户可定义
  * 使用强化学习的方法，训练模型
  * 可能得到多个不同的图样，返回最大差异的图样
  * 默认频率的范围，用户可以手动确认
* 支持在台阶处的特殊处理
