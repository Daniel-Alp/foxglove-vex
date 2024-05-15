from collections import deque
from typing import Type

import google.protobuf.message
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor import FileDescriptor

def build_file_descriptor_set(message_class: Type[google.protobuf.message.Message]) -> FileDescriptorSet:
    file_descriptor_set = FileDescriptorSet()
    seen_dependencies = set()

    queue = deque()
    queue.append(message_class.DESCRIPTOR.file)
    
    while queue:
        next: FileDescriptor = queue.popleft()
        next.CopyToProto(file_descriptor_set.file.add())

        for dep in next.dependencies: 
            if dep.name not in seen_dependencies:
                seen_dependencies.add(dep.name)
                queue.append(dep)

    return file_descriptor_set