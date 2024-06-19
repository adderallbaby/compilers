package main
import (
    "fmt"
    "time"
)

func d(from string){
  go fmt.Println("yes")
}
func main() {

    f("direct")

    go f("goroutine")
    d("goroutine")
    go func(msg string) {
        fmt.Println(msg)
    }("going")

    time.Sleep(time.Second)
    fmt.Println("done")
}
