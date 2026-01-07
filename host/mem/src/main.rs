use tapasco::tlkm::*;
use std::collections::HashMap;
use thiserror::Error;
use clap::Parser;

#[derive(Error, Debug)]
pub enum TapascoError {
    #[error("io error")]
    IO(#[from] std::io::Error),
    #[error("utf8 error")]
    UTF8(#[from] std::string::FromUtf8Error),
    #[error("Allocator Error")]
    Allocator(#[from] tapasco::allocator::Error),
    #[error("DMA Error")]
    DMA(#[from] tapasco::dma::Error),
    #[error("Failed to initialize TLKM object")]
    TLKMInit(#[from] tapasco::tlkm::Error),
    #[error("Failed to decode TLKM device")]
    DeviceInit(#[from] tapasco::device::Error),
    #[error("Error while executing Job")]
    JobError(#[from] tapasco::job::Error),
}

#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Mode
    #[arg(short, long, value_name = "FILE", default_value_t = 0)]
    mode: u32,
    /// Address
    #[arg(short, long, value_name = "FILE", default_value_t = 0)]
    addr: u32,
    /// Count
    #[arg(short, long, value_name = "FILE", default_value_t = 0)]
    count: u32,
    /// Data
    #[arg(short, long, value_name = "FILE", default_value_t = 0)]
    data: u32,
    /// Jobs
    #[arg(short, long, value_name = "FILE", default_value_t = 1)]
    jobs: usize,
}

fn main() -> Result<(), TapascoError> {
    let cli = Cli::parse();

    let tlkm = TLKM::new()?;
    println!("TLKM version is {}", tlkm.version()?);
    let devices = tlkm.device_enum(&HashMap::new())?;
    for mut device in devices {
        println!(
            "Device {}: Name: {}, Vendor: {}, Product {}, Status{:?}",
            device.id(),
            device.name(),
            device.vendor(),
            device.product(),
            device.status()
        );
        device.change_access(tapasco::tlkm::tlkm_access::TlkmAccessExclusive)?;

        let pe_id = match device.get_pe_id("esa.informatik.tu-darmstadt.de:user:array_init_update_sum:1.0") {
            Ok(x) => x,
            Err(_e) => continue,
        };
        println!("pe found: {}", pe_id);

        println!("start");
        let mut pes = Vec::new();
        for _ in 0..cli.jobs {
            let mut pe = device.acquire_pe(pe_id)?;
            pe.start(vec![
                tapasco::device::PEParameter::Single32(cli.mode),
                tapasco::device::PEParameter::Single32(cli.addr),
                tapasco::device::PEParameter::Single32(cli.count),
                tapasco::device::PEParameter::Single32(cli.data),
            ])?;
            pes.push(pe);
        }

        println!("run");
        for i in 0..cli.jobs {
            let (result, _output) = pes[i].release(true, true)?;
            println!("> {}", result);
        }
    }
    println!("exit");
    Ok(())
}

