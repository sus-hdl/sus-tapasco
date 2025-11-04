use tapasco::tlkm::*;
use std::collections::HashMap;
use thiserror::Error;

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

fn main() -> Result<(), TapascoError> {
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

        let pe_id = match device.get_pe_id("esa.informatik.tu-darmstadt.de:user:example:1.0") {
            Ok(x) => x,
            Err(_e) => continue,
        };
        println!("pe found: {}", pe_id);
        let mut pe = device.acquire_pe(pe_id)?;

        println!("start");
        pe.start(vec![
            tapasco::device::PEParameter::Single32(4),
            tapasco::device::PEParameter::Single32(6),
        ])?;
        let (result, output) = pe.release(true, false)?;
        println!("done {:?}", result);
    }
    println!("exit");
    Ok(())
}