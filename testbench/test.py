#!/usr/bin/env python
import cocotb
import random
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.binary import BinaryValue

async def clock(dut, cycles):
    for cycle in range(cycles):
        dut.aclk.value = 0
        await Timer(500, units="ps")
        dut.aclk.value = 1
        await Timer(500, units="ps")

def set_unassigned(signal):
    signal.value = BinaryValue("X" * len(signal), n_bits=len(signal))

class Axi4Lite:

    def __init__(self, dut, clk, prefix: str):
        self.clk = clk
        self.awaddr = dut._id(f'{prefix}awaddr', extended=False)
        self.awprot = dut._id(f'{prefix}awprot', extended=False)
        self.awvalid = dut._id(f'{prefix}awvalid', extended=False)
        self.awready = dut._id(f'{prefix}awready', extended=False)
        self.wdata = dut._id(f'{prefix}wdata', extended=False)
        self.wstrb = dut._id(f'{prefix}wstrb', extended=False)
        self.wvalid = dut._id(f'{prefix}wvalid', extended=False)
        self.wready = dut._id(f'{prefix}wready', extended=False)
        self.bresp = dut._id(f'{prefix}bresp', extended=False)
        self.bvalid = dut._id(f'{prefix}bvalid', extended=False)
        self.bready = dut._id(f'{prefix}bready', extended=False)
        self.araddr = dut._id(f'{prefix}araddr', extended=False)
        self.arprot = dut._id(f'{prefix}arprot', extended=False)
        self.arvalid = dut._id(f'{prefix}arvalid', extended=False)
        self.arready = dut._id(f'{prefix}arready', extended=False)
        self.rdata = dut._id(f'{prefix}rdata', extended=False)
        self.rresp = dut._id(f'{prefix}rresp', extended=False)
        self.rvalid = dut._id(f'{prefix}rvalid', extended=False)
        self.rready = dut._id(f'{prefix}rready', extended=False)

        self.awvalid.value = False
        set_unassigned(self.awaddr)
        set_unassigned(self.awprot)
        self.wvalid.value  = False
        set_unassigned(self.wdata)
        set_unassigned(self.wstrb)
        self.bready.value  = False
        self.arvalid.value = False
        set_unassigned(self.araddr)
        set_unassigned(self.arprot)
        self.rready.value  = False

    async def aw(self, addr):
        self.awaddr.value = addr
        self.awprot.value = 0
        self.awvalid.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.awready.value:
                break
        self.awvalid.value = False
        set_unassigned(self.awaddr)
        set_unassigned(self.awprot)

    async def w(self, data, strb = -1):
        self.wdata.value = data
        self.wstrb.value = strb
        self.wvalid.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.wready.value:
                break
        self.wvalid.value = False
        set_unassigned(self.wdata)
        set_unassigned(self.wstrb)

    async def b(self):
        self.bready.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.bvalid.value:
                break
        self.bready.value = False

    async def ar(self, addr):
        self.araddr.value = addr
        self.arprot.value = 0
        self.arvalid.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.arready.value:
                break
        self.arvalid.value = False
        set_unassigned(self.araddr)
        set_unassigned(self.arprot)

    async def r(self):
        self.rready.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.rvalid.value:
                break
        self.rready.value = False
        return self.rdata.value


async def reset(dut):
    dut.aresetn.value = False
    await RisingEdge(dut.aclk)
    await RisingEdge(dut.aclk)
    await RisingEdge(dut.aclk)
    dut.aresetn.value = True

@cocotb.test()
async def test(dut):
    dut.aclk.value = 0
    dut.aresetn.value = 0
    ctrl = Axi4Lite(dut, dut.aclk, 's_axi_control_')
    clk = cocotb.start_soon(clock(dut, 30))
    await reset(dut)

    cocotb.start_soon(ctrl.aw(0x20))
    cocotb.start_soon(ctrl.w(4))
    await ctrl.b()

    cocotb.start_soon(ctrl.aw(0x28))
    cocotb.start_soon(ctrl.w(0))
    await ctrl.b()

    cocotb.start_soon(ctrl.aw(0x30))
    cocotb.start_soon(ctrl.w(6))
    await ctrl.b()

    cocotb.start_soon(ctrl.aw(0))
    cocotb.start_soon(ctrl.w(1))
    await ctrl.b()

    #while True:
    #    await RisingEdge(dut.aclk)
    #    if dut.intr.value:
    #        break

    cocotb.start_soon(ctrl.ar(0x20))
    arg0 = await ctrl.r()
    cocotb.start_soon(ctrl.ar(0x30))
    arg1 = await ctrl.r()
    cocotb.start_soon(ctrl.ar(0x10))
    result = await ctrl.r()
    print(f'{int(arg0)} + {int(arg1)} = {int(result)}')

    await clk
    print("done")
