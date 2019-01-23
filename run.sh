docker run -t --rm --name selenuim -v "$PWD":/usr/src/myapp -v /dev/shm:/dev/shm -w /usr/src/myapp <you_name>/selenium python $1
