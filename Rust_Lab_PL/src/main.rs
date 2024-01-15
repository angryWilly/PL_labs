extern crate reqwest;
extern crate colored;
extern crate indicatif;

use std::env;
use std::fs::File;
use std::io::prelude::*;
use std::process;
use std::error::Error;
use indicatif::{ProgressBar, ProgressStyle};
use reqwest::blocking::get;
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread::{self, sleep};
use std::time::Duration;
use colored::*;

fn create_bar(x: u64) -> ProgressBar {
    let bar=ProgressBar::new(x);
    bar.set_style(ProgressStyle::with_template("{spinner.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {bytes}/{total_bytes} ({eta})")
    .unwrap()
    .progress_chars("#>-"));
    
    return bar;
}

fn download(url: &str) -> Result<(), Box<dyn Error>>{
    let mut response = get(url)?;
    
    if !response.status().is_success() {
        return Err("Error fetching file!".into());
    }

    let name = url.split("/").last().unwrap();
    let mut file=File::create(name).unwrap();

    let content_length = response.content_length().unwrap();

    let progress = Arc::new(AtomicU64::new(0));
    let progress_clone = progress.clone();

    let download_thread = thread::spawn(
        move || {

        let mut buf: Vec<u8> = Vec::new();
        loop {
            let mut buf2: Vec<u8> = vec![0; 1024];
            let bytes = response.read(&mut buf2).unwrap();
            buf2.truncate(bytes);

            if bytes == 0 {
                break;
            }
    
            buf.append(&mut buf2);

            progress.fetch_add(bytes as u64, Ordering::Relaxed);
        }

        file.write_all(&mut buf).unwrap();
    });

    println!("Downloading {}", name.green());
    let progress_bar= create_bar(content_length);

    loop {
        let bytes = progress_clone.load(Ordering::Relaxed);

        if bytes == content_length {
            break;
        }

        progress_bar.set_position(bytes as u64);
        sleep(Duration::from_secs(1));
    }
    
    progress_bar.finish();
    download_thread.join().unwrap();
    println!("\n{}","Success!".green());

    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        println!("Usage: {} <url>", args[0]);
        return;
    }

    let url = &args[1];
    
    if let Err(e) = download(url){
        eprintln!("{}", e.to_string().red());
        process::exit(1);
    }
}