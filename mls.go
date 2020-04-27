// mls

package main

import (
	"flag"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
)

// FLAGS - Change default values @ parseFlags()
var lazyLoading bool
var publicDir string
var portNumber int

// STRUCTS - Datatypes for server
type endpoint struct { // contains file information
	fileInfo     os.FileInfo
	fileName     string
	dir          string // local directory
	address      string // web relative directory (does not include publicdir)
	contentType  string
	content      []byte
	visitCounter int
}

type broadcast struct { // contains information related to server-wide operations
	subdir     []string
	endpoints  []endpoint
	portString string
}

func main() {
	parseFlags()

	PUBLIC := broadcast{
		endpoints:  nil,
		portString: ":" + strconv.Itoa(portNumber),
		subdir:     []string{},
	}

	PUBLIC.addSubDir(publicDir)
	PUBLIC.subdir = append(PUBLIC.subdir, publicDir)

	for _, subdir := range PUBLIC.subdir {
		fileInfos, _ := ioutil.ReadDir(subdir)
		for i := 0; i < len(fileInfos); i++ {
			var data []byte
			var err error
			if fileInfos[i].IsDir() {
				continue
			}
			if !lazyLoading {
				data, err = ioutil.ReadFile(subdir + "/" + fileInfos[i].Name())
				if err != nil {
					log.Fatal("Failed to read " + fileInfos[i].Name() + "  @  " + subdir)
				}
			}
			PUBLIC.endpoints = append(PUBLIC.endpoints, endpoint{
				fileInfo:     fileInfos[i],
				fileName:     fileInfos[i].Name(),
				dir:          subdir,
				address:      strings.TrimPrefix(strings.TrimPrefix(subdir, publicDir), "/"),
				contentType:  getContentType(fileInfos[i].Name()),
				content:      data,
				visitCounter: 0,
			})
		}
	}

	if len(PUBLIC.endpoints) <= 0 {
		log.Fatal("Did not find public directory or no contents")
	}
	// Begin SERVER
	log.Println("Creating endpoints...")
	for i := 0; i < len(PUBLIC.endpoints); i++ {
		epPointer := &PUBLIC.endpoints[i]
		address := epPointer.fileAddress()
		log.Println("CREATE " + epPointer.fileName + " accessible by localhost" + PUBLIC.portString + address)
		http.HandleFunc(address, func(w http.ResponseWriter, request *http.Request) {
			w.Header().Add("Content-Type", epPointer.contentType)
			if lazyLoading {
				w.Write(epPointer.getFileData())
			} else {
				w.Write(epPointer.content)
			}
			epPointer.visitCounter++
			log.Println(epPointer.fileName+" visit #", epPointer.visitCounter, "\nUserAgent:", request.Header["User-Agent"])
		})
	}
	log.Println("All endpoints created.")
	log.Println("Starting server on port " + PUBLIC.portString)
	log.Fatal(http.ListenAndServe(PUBLIC.portString, nil))
}

func parseFlags() {
	flag.BoolVar(&lazyLoading, "lazy", true, "Enables/disables lazy loading of files.")
	flag.IntVar(&portNumber, "p", 8080, "Port number for broadcasting server.")
	flag.StringVar(&publicDir, "dir", "public", "Directory for broadcasting server.")
	flag.Parse()
}

func (ep *endpoint) getFileData() []byte {
	data, err := ioutil.ReadFile(ep.filePath())
	if err != nil {
		log.Fatal("Failed to read " + ep.fileName + "  @  " + ep.dir)
	}
	return data
}

func (ep *endpoint) loadContent() {
	data, err := ioutil.ReadFile(ep.filePath())
	if err != nil {
		log.Fatal("Failed to read " + ep.fileName + "  @  " + ep.dir)
	}
	ep.content = data
}

func (ep *endpoint) filePath() string {
	return ep.dir + "/" + ep.fileName
}

func (ep *endpoint) fileAddress() string {
	if ep.address == "" {
		if ep.fileName == "index.html" {
			return "/"
		}
		return "/" + ep.fileName
	} else {
		return "/" + ep.address + "/" + ep.fileName
	}
}

func getContentType(filename string) string {
	var contentType string
	fileTypeIndex := strings.LastIndex(filename, ".")
	if fileTypeIndex == -1 || len(filename) == fileTypeIndex+1 { // si el nombre termina con un punto (is that even legal?)
		contentType = "application/octet-stream"
		return contentType // Or next part errors!
	}
	ext := filename[fileTypeIndex+1:] // file extension
	switch ext {
	// Typical Web stuff
	case "js", "mjs":
		contentType = "application/javascript"
	case "css", "csv":
		contentType = "text/" + ext
	case "html", "htm":
		contentType = "text/html"

		// APPLICATION AND STUFF
	case "7z":
		contentType = "application/x-7z-compressed"
	case "zip", "rtf", "json", "xml", "pdf":
		contentType = "application/" + ext
	case "gz":
		contentType = "application/gzip"
	case "rar":
		contentType = "application/vnd.rar"
	case "doc":
		contentType = "application/msword"
	case "docx":
		contentType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
	case "ppt":
		contentType = "application/vnd.ms-powerpoint"
	case "pptx":
		contentType = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
	case "xls":
		contentType = "application/vnd.ms-excel"
	case "xlsx":
		contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
	case "xhtml":
		contentType = "application/xhtml+xml"
	case "sh", "csh":
		contentType = "application/x-" + ext

		// FONT
	case "ttf", "otf", "woff", "woff2":
		contentType = "font/" + ext

		// AUDIO
	case "wav", "aac", "opus":
		contentType = "audio/" + ext
	case "mp3":
		contentType = "audio/mpeg"

		// IMAGE
	case "bmp", "gif", "png", "webp":
		contentType = "image/" + ext
	case "tif", "tiff":
		contentType = "image/tiff"
	case "svg":
		contentType = "image/svg+xml"
	case "jpg", "jpeg":
		contentType = "image/jpeg"
	case "ico":
		contentType = "image/x-icon"

		// VIDEO
	case "ts":
		contentType = "video/mp2t"
	case "avi":
		contentType = "video/x-msvideo"
	case "mp4", "webm", "mpeg":
		contentType = "video/" + ext

		// Plaintext
	case "txt", "dat", "md", ".gitignore":
		contentType = "text/plain"
	case "go", "h", "c", "py", "tex", "sty", "m": // program
		contentType = "text/plain"
	default:
		contentType = "application/octet-stream"
	}
	return contentType
}

func (bc *broadcast) addSubDir(dirpath string) {
	currDir, err := ioutil.ReadDir(dirpath)
	if err != nil {
		log.Fatal("Could not read directory " + dirpath + ".")
	}
	for _, fileInfo := range currDir {
		if fileInfo.IsDir() {
			bc.subdir = append(bc.subdir, dirpath+"/"+fileInfo.Name())
			bc.addSubDir(dirpath + "/" + fileInfo.Name())
		}
	}
}
