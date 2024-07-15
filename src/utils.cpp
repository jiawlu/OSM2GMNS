//
// Created by Jiawei Lu on 2/16/23.
//

#include "utils.h"

#include "absl/base/log_severity.h"
#include "absl/log/globals.h"
#include "absl/log/initialize.h"

void initializeAbslLogging() {
  absl::InitializeLog();
  absl::SetStderrThreshold(absl::LogSeverityAtLeast::kInfo);
};