rm(list=ls())

Args <- commandArgs(trailingOnly = TRUE)

# stub_dir = "/Users/adyke/Vizuri/"
# IStubfilename = "IStub2015.txt"
# DStubfilename = "DStub2015.txt"
# IntStubfilename = "IntStub2015.txt"

stub_dir = Args[1]
IStubfilename = Args[2]
DStubfilename = Args[3]
IntStubfilename = Args[4]

convertStubFiles <- function(dir = stub_dir){
  try(setwd(dir))
  fileNaming <- c("IStub","DStub","IntStub")
  for(s in c(IStubfilename, DStubfilename, IntStubfilename)) {
    
    # Read in the original stub file, keep only the first line of every entry,
    # and substitute 2 tabs for 7 spaces
    sp <- paste0(s)
    sf <- readLines(sp)
    sf <- gsub("\t\t" , "       " , sf)
    
    # Put the stub file in a temporary file
    tf <- tempfile()
    writeLines(sf, tf)
    
    # Read in the cleaner version of the stub file in fixed-width format
    stub <- read.fwf(
      tf, width = c(1, -2, 1, -2, 60, -3, 6, -7, 1, -5, 7),
      col.names = c("type", "level", "title", "UCC", "survey", "group")
    )
    
    # Convert the stub file to a data frame and strip whitespace
    stub[, names(Filter(is.factor, stub))] <-
      data.frame(lapply(stub[, names(Filter(is.factor, stub))], as.character),
                 stringsAsFactors = FALSE)
    
    trim.leading <- function(x) sub("^\\s+", "", x)
    trim.trailing <- function(x) sub("\\s+$", "", x)
    
    stub <- data.frame(lapply(stub, trim.leading), stringsAsFactors = FALSE)
    stub <- data.frame(lapply(stub, trim.trailing), stringsAsFactors = FALSE)
    
    # Concatenate the titles that run beyond 1 line into their respective first
    # lines
    for (i in seq(length(stub$type))) {
      if (stub$type[i] %in% "2") {
        l1_row <- max(which(stub$type[1:i] %in% "1"))
        stub$title[l1_row] <- paste(stub$title[l1_row], stub$title[i])
      }
    }
    
    stub <- stub[stub$type %in% c("1", "*"), ]
    
    # Make all the variable names lower character
    names(stub) <- tolower(names(stub))
    
    # copy the stub file into the global environment
    assign(fileNaming[which(s == c(IStubfilename, DStubfilename, IntStubfilename))], stub, envir = .GlobalEnv)
  }
  
}

convertStubFiles(dir = stub_dir)
write.csv(DStub, file = "DStub.csv")
write.csv(IStub, file = "IStub.csv")
write.csv(IntStub, file = "IntStub.csv")

