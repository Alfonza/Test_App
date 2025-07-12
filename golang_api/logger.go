package main

import (
	"os"
	"runtime/debug"
	"time"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

var logger zerolog.Logger

func init_logger() {
	logger_file, err := os.OpenFile("logs.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to open log file")
	}
	console_writer := zerolog.ConsoleWriter{Out: os.Stdout, TimeFormat: time.RFC3339}
	multi_writer := zerolog.MultiLevelWriter(console_writer, logger_file)
	logger = zerolog.New(multi_writer).With().Timestamp().Logger()
}
func LogErrorWithStack(err error, message string) {
	if err != nil {
		logger.Error().
			Str("error", err.Error()).
			Str("stack_trace", string(debug.Stack())). // Capture full stack trace
			Msg(message)
	}
}
