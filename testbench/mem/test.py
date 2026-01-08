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

class Axi4Memory:

    def __init__(self, dut, clk, prefix: str):
        self.clk = clk
        self.awaddr = dut._id(f'{prefix}awaddr', extended=False)
        self.awlen = dut._id(f'{prefix}awlen', extended=False)
        self.awprot = dut._id(f'{prefix}awprot', extended=False)
        self.awvalid = dut._id(f'{prefix}awvalid', extended=False)
        self.awready = dut._id(f'{prefix}awready', extended=False)
        self.wdata = dut._id(f'{prefix}wdata', extended=False)
        self.wstrb = dut._id(f'{prefix}wstrb', extended=False)
        self.wlast = dut._id(f'{prefix}wlast', extended=False)
        self.wvalid = dut._id(f'{prefix}wvalid', extended=False)
        self.wready = dut._id(f'{prefix}wready', extended=False)
        self.bresp = dut._id(f'{prefix}bresp', extended=False)
        self.bvalid = dut._id(f'{prefix}bvalid', extended=False)
        self.bready = dut._id(f'{prefix}bready', extended=False)
        self.araddr = dut._id(f'{prefix}araddr', extended=False)
        self.arlen = dut._id(f'{prefix}arlen', extended=False)
        self.arprot = dut._id(f'{prefix}arprot', extended=False)
        self.arvalid = dut._id(f'{prefix}arvalid', extended=False)
        self.arready = dut._id(f'{prefix}arready', extended=False)
        self.rdata = dut._id(f'{prefix}rdata', extended=False)
        self.rresp = dut._id(f'{prefix}rresp', extended=False)
        self.rvalid = dut._id(f'{prefix}rvalid', extended=False)
        self.rlast = dut._id(f'{prefix}rlast', extended=False)
        self.rready = dut._id(f'{prefix}rready', extended=False)

        self.awready.value = False
        self.wready.value  = False
        self.bvalid.value  = False
        set_unassigned(self.bresp)
        self.arready.value = False
        self.rvalid.value  = False
        set_unassigned(self.rresp)
        set_unassigned(self.rdata)
        set_unassigned(self.rlast)

        self.memory = dict()

    async def handle_writes(self):
        aw = cocotb.start_soon(self.get_next_aw())
        while True:
            addr, length = await aw
            aw = cocotb.start_soon(self.get_next_aw())
            await self.handle_write(addr, length)

    async def get_next_aw(self):
        # addr
        self.awready.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.awvalid.value:
                addr = int(self.awaddr.value)
                length = int(self.awlen.value)
                break
        self.awready.value = False
        await (RisingEdge(self.clk))
        return addr, length

    async def handle_write(self, addr, length):
        # addr
        print(f"w {addr} {length}")
        for i in range(10):
            await (RisingEdge(self.clk))

        # data
        self.wready.value = True
        while length >= 0:
            await (RisingEdge(self.clk))
            if self.wvalid.value:
                self.memory[addr] = self.wdata.value
                print(f">w {addr} {length} {int(self.wdata.value) & 0xffffffff} {self.wlast.value}")
                addr += len(self.wstrb)
                length -= 1
        self.wready.value = False

        # resp
        self.bvalid.value = True
        self.bresp.value = 0b00
        while True:
            await (RisingEdge(self.clk))
            if self.bready.value:
                break
        self.bvalid.value = False
        set_unassigned(self.bresp)

    async def handle_reads(self):
        ar = cocotb.start_soon(self.get_next_ar())
        while True:
            addr, length = await ar
            ar = cocotb.start_soon(self.get_next_ar())
            await self.handle_read(addr, length)

    async def get_next_ar(self):
        # addr
        self.arready.value = True
        while True:
            await (RisingEdge(self.clk))
            if self.arvalid.value:
                addr = int(self.araddr.value)
                length = int(self.arlen.value)
                break
        self.arready.value = False
        await (RisingEdge(self.clk))
        return addr, length

    async def handle_read(self, addr, length):
        # addr
        print(f"r {addr} {length}")
        for i in range(10):
            await (RisingEdge(self.clk))

        # data
        self.rdata.value = self.memory[addr] if addr in self.memory else 0
        self.rresp.value = 0b00
        self.rvalid.value = True
        self.rlast.value = length == 0
        while length >= 0:
            await (RisingEdge(self.clk))
            if self.rready.value:
                addr += len(self.wstrb)
                self.rdata.value = self.memory[addr] if addr in self.memory else 0
                length -= 1
                self.rlast.value = length == 0
        self.rvalid.value = False
        set_unassigned(self.rresp)
        set_unassigned(self.rdata)
        set_unassigned(self.rlast)


async def reset(dut):
    dut.aresetn.value = False
    await RisingEdge(dut.aclk)
    await RisingEdge(dut.aclk)
    await RisingEdge(dut.aclk)
    dut.aresetn.value = True

async def run(clk, ctrl, intr, mode, addr, count, data):
    # mode
    cocotb.start_soon(ctrl.aw(0x20))
    cocotb.start_soon(ctrl.w(mode))
    await ctrl.b()
    # addr
    cocotb.start_soon(ctrl.aw(0x30))
    cocotb.start_soon(ctrl.w(addr))
    await ctrl.b()
    # count
    cocotb.start_soon(ctrl.aw(0x40))
    cocotb.start_soon(ctrl.w(count))
    await ctrl.b()
    # data
    cocotb.start_soon(ctrl.aw(0x50))
    cocotb.start_soon(ctrl.w(data))
    await ctrl.b()
    # start
    cocotb.start_soon(ctrl.aw(0))
    cocotb.start_soon(ctrl.w(1))
    await ctrl.b()

    while True:
        await RisingEdge(clk)
        if intr.value:
            break

    cocotb.start_soon(ctrl.ar(0x10))
    result = await ctrl.r()
    print(f'result: {int(result)}')

@cocotb.test()
async def test(dut):
    dut.aclk.value = 0
    dut.aresetn.value = 0
    ctrl = Axi4Lite(dut, dut.aclk, 'saxi_control_')
    maxi = Axi4Memory(dut, dut.aclk, 'maxi_')
    clk = cocotb.start_soon(clock(dut, 2000))
    await reset(dut)

    mem_writes = cocotb.start_soon(maxi.handle_writes())
    mem_reads = cocotb.start_soon(maxi.handle_reads())

   # await run(dut.aclk, ctrl, dut.intr, 0, 0, 256, 0)
    await run(dut.aclk, ctrl, dut.intr, 0, 128, 256, 0)
    for _ in range(200):
        await RisingEdge(dut.aclk)
    await run(dut.aclk, ctrl, dut.intr, 1, 128, 256, 10)
    for _ in range(200):
        await RisingEdge(dut.aclk)
    await run(dut.aclk, ctrl, dut.intr, 2, 128, 256, 0)
    for _ in range(200):
        await RisingEdge(dut.aclk)

    await clk
    print("done")
