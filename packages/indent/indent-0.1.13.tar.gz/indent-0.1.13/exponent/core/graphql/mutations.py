HALT_CHAT_STREAM_MUTATION: str = """
  mutation HaltChatStream($chatUuid: UUID!) {
    haltChatStream(chatUuid: $chatUuid) {
      __typename
    }
  }
"""


SET_LOGIN_COMPLETE_MUTATION: str = """
  mutation SetLoginComplete {
    setLoginComplete {
      __typename
      ... on User {
        userApiKey
      }
      ... on UnauthenticatedError {
        message
      }
    }
  }
"""


REFRESH_API_KEY_MUTATION = """
mutation RefreshApiKey {
    refreshApiKey {
        ... on User {
            userApiKey
        }
        ... on UnauthenticatedError {
            message
        }
    }
}
"""

START_CHAT_TURN_MUTATION = """
mutation StartChatTurnMutation($chatInput: ChatInput!, $parentUuid: String, $chatConfig: ChatConfig!) {
    startChatReply(
        chatInput: $chatInput,
        parentUuid: $parentUuid,
        chatConfig: $chatConfig
    ) {
      __typename
      ... on UnauthenticatedError {
          message
      }
      ... on ChatNotFoundError {
          message
      }
      ... on Chat {
          chatUuid
      }
  }
}
"""


CREATE_CLOUD_CHAT_MUTATION = """
mutation CreateCloudChat($configId: String!) {
  createCloudChat(cloudConfigUuid: $configId) {
    __typename
    ...on Chat {
      chatUuid
    }
    ...on CloudSessionError {
      message
    }
    ...on UnauthenticatedError {
      message
    }
  }
}
"""


CREATE_CLOUD_CHAT_FROM_REPOSITORY_MUTATION = """
mutation CreateCloudChatFromRepository($repositoryId: String!) {
  createCloudChat(repositoryId: $repositoryId) {
    __typename
    ...on Chat {
      chatUuid
    }
    ...on UnauthenticatedError {
      message
    }
    ...on ChatNotFoundError {
      message
    }
    ...on CloudConfigNotFoundError {
      message
    }
    ...on GithubConfigNotFoundError {
      message
    }
    ...on CloudSessionError {
      message
    }
  }
}
"""


ENABLE_CLOUD_REPOSITORY_MUTATION = """
mutation EnableCloudRepository($orgName: String!, $repoName: String!) {
  enableCloudRepository(orgName: $orgName, repoName: $repoName) {
    __typename
    ...on ContainerImage {
      buildRef
      createdAt
      updatedAt
    }
    ...on UnauthenticatedError {
      message
    }
    ...on CloudConfigNotFoundError {
      message
    }
    ...on GithubConfigNotFoundError {
      message
    }
    ...on CloudSessionError {
      message
    }
    ...on Error {
      message
    }
  }
}
"""


INCREMENTAL_BUILD_CLOUD_REPOSITORY_MUTATION = """
mutation IncrementalBuildCloudRepository($orgName: String!, $repoName: String!) {
  incrementalBuildCloudRepository(orgName: $orgName, repoName: $repoName) {
    __typename
    ...on ContainerImage {
      buildRef
      createdAt
      updatedAt
    }
    ...on UnauthenticatedError {
      message
    }
    ...on CloudConfigNotFoundError {
      message
    }
    ...on GithubConfigNotFoundError {
      message
    }
    ...on CloudSessionError {
      message
    }
    ...on Error {
      message
    }
  }
}
"""


REBUILD_CLOUD_REPOSITORY_MUTATION = """
mutation RebuildCloudRepository($orgName: String!, $repoName: String!) {
  rebuildCloudRepository(orgName: $orgName, repoName: $repoName) {
    __typename
    ...on ContainerImage {
      buildRef
      createdAt
      updatedAt
    }
    ...on UnauthenticatedError {
      message
    }
    ...on CloudConfigNotFoundError {
      message
    }
    ...on GithubConfigNotFoundError {
      message
    }
    ...on CloudSessionError {
      message
    }
    ...on Error {
      message
    }
  }
}
"""
